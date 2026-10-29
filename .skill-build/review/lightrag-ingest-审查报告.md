# lightrag-ingest 技能审查报告

- 审查对象：`~/.agents/skills/lightrag-ingest`（源副本：`/Users/miguoqing/LightRAG/.skill-build/lightrag-ingest`）
- 审查时间：2026-10-29
- 审查方式：通读 `SKILL.md` + `scripts/ingest_file.py`，对照本机 LightRAG v1.5.8 的真实 API 行为做灰度验证（未破坏现有知识库）

---

## 一、总体结论

**主流程可用，但还不能放心长期使用。**

今天用它真实入库了《打卡管理.html》，一次成功：`processed`、18 个分块、141 个实体节点、169 条关系边，随后检索“打卡方式”能正确召回三种方式。说明「试运行 → 确认 → 上传 → 轮询 → 报告」这条主链路是通的，架构选择（走 HTTP 而不是进程内 new 一个 LightRAG）也是对的。

问题集中在**失败路径**和**边界类型**：三个功能缺陷（`--replace` 失效、二进制文件 token 预估失真、缺“失败即清理”），加上若干健壮性与文档准确性问题。

评分（10 分制）：功能完整度 **8**，健壮性 **6**，文档准确性 **7**。

---

## 二、做得好的地方（建议保留）

1. **只读与写入严格分离**：`inspect` 不发任何写请求，确认表让人先看清 token 与目标路径。
2. **上传前就挡住不支持的后缀**：先查 `GET /documents/supported_file_types`，比上传后吃 400 更省事。
3. **中文一致**：确认表、结果、失败建议全是中文，且保留了 `HTTP 409`、`track_id` 这类不能翻译的标识。
4. **架构正确**：HTTP 上传让服务端自己解析/切分/抽取，避开了 NetworkX 单写者冲突。
5. **失败建议具体**：不是“失败了”，而是给出 409/413/400/401 各自的动作。

---

## 三、必须修复（P0 / P1）

### P1-1 `--replace` 实际不生效，而且静默失败

**证据**

```
文档记录：id = doc-257b5fe42805aae06dd4a3d3f8813a3a，file_path = 打卡管理.html
```

脚本里 `delete_document(base_url, path.name)` 把文件名当成了 `doc_id`。而

```
DELETE /documents/delete_document  {"doc_ids":["no-such-id"]}
→ 200 {"status":"deletion_started"}
```

该接口**异步且不校验存在性**，所以删一个不存在的 id 也返回成功。结果：`--replace` 删除的是空气，重新上传仍然 409，用户却以为已经替换。

**影响**：同名文档永远换不掉，只能去 WebUI 手删。

**修复**：409 时先 `POST /documents/paginated` 按 `file_path` 反查真实 id，再 `DELETE /documents/delete_document`（带 `delete_llm_cache=true`），轮询到该 id 消失后再上传。

### P1-2 二进制类型（xlsx/pptx/epub/odt…）的 token 预估是垃圾数据

**证据**

```
$ 4 KB 随机字节，命名 fake.epub
文件：fake.epub
文档类型：auto
预估 token：≈ 3,072（正文 3,769 字符）
```

**原因**：`extract_text()` 对非 pdf/docx 的文件一律 `read_text(encoding="utf-8", errors="replace")`，二进制被替换字符撑成了“正文”。

**影响**：确认表里最关键的数字失真，用户据此判断要不要入库会被误导；而这些类型恰恰是 `auto` 分支的主要成员。

**修复**：只对文本类后缀（`.md/.txt/.json/.yaml/.yml/.html/.csv/.xml/.log` 等）走 `read_text`；其余 `auto` 类型返回 `None, "二进制文件，交由服务端解析"`，token 显示“未知”，并附一句“无法本地预估”。

### P1-3 没有“失败即清理”，与你的使用要求不一致

**现状**：脚本没有 purge 能力，`SKILL.md` 也没有这条规则。一旦上传失败、处理 `failed` 或中途异常，会在 `doc_status`、`text_chunks`、向量库、`full_entities/full_relations` 锚点、`inputs/__parsed__` 里留下半成品。今天这次成功，所以没暴露；失败一次就会脏。

**修复**：加 `--purge-on-failure`（或独立 `purge <file>` 子命令），行为固定为：

1. 按 `file_path` 反查真实 `doc_id`；
2. `DELETE /documents/delete_document`（`delete_file=true`、`delete_llm_cache=true`）；
3. 轮询 `/documents/paginated` 直到该文档消失；
4. 清理 `inputs/__parsed__/<name>*`；
5. 输出逐项核对结果（文档记录 ✓ / 分块 ✓ / 解析残留 ✓）。

---

## 四、建议改进（P2 / P3）

| 级别 | 问题 | 证据 / 说明 | 建议 |
|---|---|---|---|
| P2 | 等待期完全静默 | `wait_for_document` 最多等 1800 秒，期间无任何输出，容易被当成卡死 | 每 15 秒往 stderr 打一行“处理中… status=processing 已用 45s” |
| P2 | 非 JSON 响应直接抛异常 | `_request` 里 `json.loads(raw)` 未捕获 `JSONDecodeError`（例如代理返回 HTML 登录页） | 捕获后包装成 `ApiError`，提示“返回内容不是 JSON” |
| P2 | 文档里写了不存在的接口 | 失败处理表写“先 `DELETE /documents/{doc_id}`”；实际只有 `DELETE /documents`（清空）和 `DELETE /documents/delete_document` | 改成正确接口，并注明要传 JSON body |
| P2 | “文件名就是文档 ID”是错的 | `id` 是 `doc-<hash>`，文件名只是**重名冲突的判定键** | 改为“文件名是重名判定的键；真实 id 是 doc-<hash>，需要反查” |
| P2 | 硬编码本机路径 | `SKILL.md` 写死 `/Users/miguoqing/LightRAG/.venv/bin/python` 与 `~/LightRAG` | 用 `LIGHTRAG_PYTHON` / `LIGHTRAG_HOME` 环境变量，回退 `python3` |
| P2 | 日志路径过期 | `_suggest` 指向 `lightrag.log`，本机已归档到 `repo-src/lightrag.log` | 改成“服务端日志（默认 `lightrag.log`，可能被移动）” |
| P3 | 成功后没有自检 | 只报 `processed` 与分块数，没证明实体真的抽出来了 | 附带实体/关系数（只读一次 `full_entities`/`full_relations` 统计即可） |
| P3 | 评估形同虚设 | `evals/evals.json` 有 3 条 prompt，无断言、从未运行 | 要么补断言跑一轮，要么删掉避免误导 |
| P3 | 批量入库不支持 | 规则要求一次一个文件 | 符合当前设计，若要批量需先改“逐个确认”的交互约定 |

---

## 五、验证记录（本次审查实际执行过的）

| 验证 | 结果 |
|---|---|
| 真实入库《打卡管理.html》 | `processed`，18 分块，141 实体 / 169 关系 |
| 检索“有几种打卡方式” | 正确召回 3 种（手机、考勤机、U 盘导入）+ 外出打卡 |
| `inspect` 二进制 `.epub` | 复现 token 失真（3,769 字符 / 3,072 token） |
| `DELETE` 不存在的 doc_id | 返回 200 `deletion_started`，证明删除不校验存在性 |
| `POST /documents/paginated` | 确认 `id` 与 `file_path` 是两个不同字段，可用于反查 |
| 路由清单 | 只有 `DELETE /documents` 与 `DELETE /documents/delete_document` |

---

## 六、建议的修复顺序

1. **P1-3 失败即清理**（你新提出的要求，优先级最高）
2. **P1-1 `--replace` 反查 id**（现成的坑，改动约 25 行）
3. **P1-2 二进制类型不猜 token**（改动约 10 行）
4. P2 一批（静默等待、JSON 兜底、文档纠错、环境变量）
5. 修完后用同一份《打卡管理.html》做一次“失败注入”验证：故意把服务地址指错，确认清理逻辑把残留清干净

预计改动量：`ingest_file.py` 约 80 行，`SKILL.md` 约 15 行。
