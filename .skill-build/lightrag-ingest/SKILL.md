---
name: lightrag-ingest
description: 把用户上传的接口文档、需求文档、缺陷报告、历史用例等文件写入本地 LightRAG 知识库并构建知识图谱。凡是用户提到“入库 / 加入知识库 / 加入知识图谱 / 构建测试知识库 / 把这个文档存进去 / 让后面能检索到它”，或者给了 .pdf/.docx/.md/.html 之类的文档并希望后续基于它检索、生成测试用例或自动化脚本时，都必须使用本技能；即使没说“入库”两个字，只要意图是把文档沉淀进知识库，也要用。默认只做试运行（dry-run：展示文件名、类型、预估 token）并等待用户确认，绝不自动写入；一切面向用户的文字用中文。
---

# LightRAG 入库

把一份文档沉淀进本地 LightRAG，让后续的检索、用例生成、脚本生成都能用到它。

入库是一次**写操作**：它会切分文档、调用大模型抽取实体与关系、写向量库和图存储，既消耗 token，也改变知识库状态。所以默认流程是
**先看清楚 → 让用户点头 → 再写**。跳过确认直接写，等于替用户花他的钱、改他的数据。

## 先决条件

1. LightRAG 服务在跑。默认 `http://127.0.0.1:9621`，可用 `LIGHTRAG_BASE_URL` 覆盖。
   连不上时不要猜，直接告诉用户如何启动（本机是 `cd ~/LightRAG && source .venv/bin/activate && bash env_openai.sh`）。
2. 用装了 `tiktoken` / `pypdf` / `python-docx` 的解释器。优先取 `LIGHTRAG_PYTHON`，没设置就用本机 `.venv`，再退回 `python3`：

   ```bash
   PY="${LIGHTRAG_PYTHON:-/Users/miguoqing/LightRAG/.venv/bin/python}"
   [ -x "$PY" ] || PY=python3
   "$PY" <skill>/scripts/ingest_file.py ...
   ```

   用 `python3` 也能跑，只是 token 会退化成“字符数/3”的粗估、PDF 会缺少文本层检测——预估仍可用，精度下降。
3. 服务开了鉴权时导出 `LIGHTRAG_API_KEY`，脚本会自动带上 `X-API-Key`。

## 操作边界

所有本地操作都限定在**项目目录**内（默认 `/Users/miguoqing/LightRAG`，可用 `--project-dir` 或 `LIGHTRAG_PROJECT_DIR` 指定）：

- **只读**用户指定的文件——文件可以在任何位置，读它是因为用户要求把它入库；
- **写/删**只发生在 `inputs/`（上传副本与 `__parsed__` 解析产物）与 `.lightrag-ingest/logs/`（操作日志）；
- **不碰** `repo-src/`、`lightrag/`、`.venv/`、`rag_storage/`，也不碰 `.git/`：不修改、不删除、不执行 `git checkout/clean`；查阅 `repo-src/docs/` 里的设计文档属于只读参考，允许。
- 知识库数据只通过 HTTP API 操作，不直接改 `rag_storage/` 里的文件——NetworkX 是单写者，直接写会覆盖服务端内存中的图；
- 脚本对越界或受保护的路径只记录、不删除（结果里体现为 `artifacts_skipped`）。

需要清理项目里的其它内容时，先说清要删什么、为什么，得到用户确认再动手。

## 全流程与日志

从“上传”到“检索”的每一步都会落一条结构化日志，用户和后续排障都靠它：

```text
.lightrag-ingest/logs/ops-YYYYMMDD.jsonl
```

每行一个事件，字段固定：`ts / run_id / command / step / action / status / detail / error / suggestion / duration_ms`。
覆盖的步骤：`inspect`（试运行）→ `ingest`（上传 / 等待 / 自检）→ `purge`（清理）→ `query`（检索 / 缺口）→ `backfill`（回补）→ `decision`（用户决策）。

- 查看：`ingest_file.py log --limit 20`；机器消费用 `--json`。
- 落盘前会脱敏（`sk-…`、`Bearer …` 一律替换为 `***`），日志可以安全贴进工单。
- 用户拍板后补一条决策记录：`ingest_file.py note "用户选择：清理 / 保留现场"`。
- 日志写入失败只降级提示，不影响主流程。

设计细节（事件模型、错误分类、决策协议）见 `references/logging.md`。

## 工作流

按顺序执行，不要跳步：

1. **定位文件**：确认用户给的是真实存在的本地路径（或刚上传落盘的文件）。路径不存在、是目录、大小 0，直接指出，不要“帮它猜一个”。
2. **试运行（dry-run，只读）**：

   ```bash
   .venv/bin/python scripts/ingest_file.py inspect <file>
   ```

   这条命令不写任何东西，只读取文件、询问服务端，算出类型与预估 token。
3. **展示确认表**（模板见下），并明确问一句“确认入库吗？”。
4. **等待确认**。只有用户明确说“确认 / 入库 / 可以”才继续。用户说“先看看”“等一下”“改成别的”时，停在试运行阶段。
5. **执行入库**：

   ```bash
   .venv/bin/python scripts/ingest_file.py ingest <file>
   ```

   默认会一直等到文档变成 `processed` 或 `failed` 再返回；文档大或服务忙时用 `--timeout 3600` 放宽。
   等待期间每 15 秒打一行进度，不会静默卡住；失败时**不清理**，先上报，等你决定（见“失败处理”）。
6. **报告结果**，并把下一步选项给出来。失败时按“失败处理”表给出原因和修复建议，不要只说“失败了”。
7. **检索（可选）**：用户要基于知识库回答问题时：

   ```bash
   .venv/bin/python scripts/ingest_file.py query "<问题>" --expect "实体A,实体B"
   ```

   `--expect` 里列出问题涉及的关键实体，脚本会逐个查图谱；缺哪个就判定为图谱缺口。
8. **缺口回补（需确认）**：发现缺口时不要自己编内容，按“图谱缺口与回补”一节处理。

### 确认表（入库前必须展示）

```text
文件：企业通讯录.html
文档类型：text
来源：/Users/miguoqing/LightRAG/企业通讯录.html（本地文件）
大小：45.2 KB
预估 token：≈ 3,214（tiktoken / cl100k_base，正文 12,345 字符）
目标知识库：/Users/miguoqing/LightRAG/rag_storage
```

“目标知识库”取服务端 `/health` 返回的 `working_directory`——那是**实际**存储位置，
不要用当前目录或 `./rag_storage` 猜。

## 文档类型

| 文件后缀 | 文档类型 | 说明 |
|---|---|---|
| .md, .mdx, .txt, .json, .yaml, .yml, .html, .htm | text | 直接读文本；html 会先剥标签再估算 |
| .pdf, .docx | document | 需要解析，估算精度取决于本机有没有 pypdf / python-docx |
| 其他（.csv/.xlsx/.pptx/...） | auto | 交给服务端解析器判断；本地不解析二进制，token 显示“未知”而不是编一个数 |

服务端是否接受某个后缀，以 `GET /documents/supported_file_types` 为准；脚本会先查一遍，
不支持就在试运行阶段拒绝，而不是等上传后才报错。

## 输出模板

入库成功：

```text
入库完成：{doc_name}
文档类型：{doc_type}
存储路径：{working_dir}
文档 ID：{doc_id}
分块数：{chunks_count}
图谱：新增实体 {n}（{before} → {after}）
下一步：可以检索知识，或生成测试用例。
```

“图谱：新增实体 0”要当成异常提示：可能抽取为空、内容重复，或实体已全部存在——不要只报“入库完成”就结束。

入库失败：

```text
入库失败：{doc_name}
失败步骤：{inspect|upload|wait}
状态：{failed|timeout}
原因：{error_msg}
建议：{fix}
旧副本：{backup_path}        # 仅 --replace 且源文件仍在时出现
重试命令：
  python ingest_file.py ingest "{file}" --timeout 3600
  python ingest_file.py ingest "{file}" --replace --timeout 3600   # 同名冲突时
清理：尚未执行 —— 需要你确认
  清理这篇文档：python ingest_file.py purge "{file}"
  保留现场：不做任何操作即可
```

失败时先给这张表，然后由用户选择“重试”还是“清理”；未得到答复前不要动任何数据。

## 失败处理：先上报，再等用户确认

任何一步失败（上传报错、处理 `failed`、等待超时）之后，**不自动清理**，按这个顺序来：

1. **上报**：失败步骤、状态、原因原文、修复建议，并说明“如果清理会删掉什么”（文档记录、上传副本、解析残留）；
2. **等用户回答**，不要自作主张；
3. 用户说“清理”→ 运行 `python ingest_file.py purge <file>`。清理逻辑本身不变：
   反查真实 `doc_id` → `DELETE /documents/delete_document`（`delete_file` 与 `delete_llm_cache` 都为 true）
   → 轮询确认记录消失 → 删除 `inputs/__parsed__/<name>*` 与上传副本；
4. 用户说“重试”→ 换参数重跑（同名冲突加 `--replace`）；
5. 用户说“先放着”→ 保留现场，什么都不做。

用户做完选择后，补一条决策记录，方便以后回溯：

```bash
python ingest_file.py note "用户选择：清理 <file>；原因：…"
```

为什么不自动清理：清理是不可逆的数据删除，而失败有时恰恰需要保留现场（解析产物、doc_status 里的半成品）才能定位原因。
自动化流水线确实需要“失败即清”时，显式加 `--purge-on-failure`，不要把它当默认。

## 缺参补齐：能推断的推断，推断不了就问

用户经常只说“把文档入库”，缺路径、缺类型、缺问题范围。处理顺序：

1. **先看上下文**：本轮对话里的附件、刚上传落盘的文件（`inputs/`）、用户上一条消息里的路径，都可以用来补齐；
2. **能确定就直接用**，并在确认表里写清依据（例如“来源：本轮上传的附件”）；
3. **不确定就问**，不要拿一个猜测去写库。典型：同名文件、多个候选路径、问题指代不清（“这个文档”指哪份）；
4. **不要虚构内容**：缺的是“字段/参数”可以推断，缺的是“事实/正文”必须问用户或走回补流程。

## 图谱缺口与回补

检索时如果答案明显不完整，或 `query --expect` 报出缺失实体，按这个流程走：

1. **先判断相关性，再谈缺口**。脚本只告诉你“图谱里有没有这些实体”，不判断该不该补：
   - **知识缺口**：问题/内容与知识库主题相关，只是缺细节 → 可以提议回补；
   - **无关内容**：根本是另一个领域（例如在考勤知识库里问量子纠缠）→ **不要回补**，只上报“知识库不覆盖”并说明原因。
   拿不准时先换 `--mode naive` 或换个说法复核，避免把“问法不对”误判成缺口。
2. **上报**：说明缺哪些实体、属于“缺口”还是“无关内容”，以及建议（补 / 不补）与代价；
3. **等确认**：回补会新增一篇文档（消耗 token），必须用户点头；无关内容默认不建议补，用户明确要求“把这个领域也纳进来”才补；
4. **回补**：

   ```bash
   python ingest_file.py backfill --text "补充内容……" --source gap-fill
   # 或
   python ingest_file.py backfill <补充文件> --source gap-fill
   ```

   补充内容必须来自用户或已有材料，**不得由模型编造**；模型可以做的是把用户口述/上下文整理成结构化文本，并在 `--source` 里标明来源；
5. **验证**：再跑一次 `query`，确认缺口补上；把结果记一条 `note`。

一句话：**回补只补“该有的知识”，不补“跑题的内容”。**

## 常见错误对照

| 现象 | 原因 | 建议 |
|---|---|---|
| `connection refused` / `URLError` | 服务没起或端口不对 | 启动服务，或用 `--base-url` 指向正确地址 |
| HTTP 409 | 同名文档已存在（文件名只是重名判定键，不是 `doc_id`） | 用 `--replace` 自动替换；或先 `DELETE /documents/delete_document`（请求体 `{"doc_ids":[真实 id]}`） |
| HTTP 413 | 超过 `MAX_UPLOAD_SIZE` | 拆分文件或调大服务端限制 |
| HTTP 400 | 后缀不在允许列表 | 转成 .md/.txt/.pdf 之一，或确认服务端解析器配置 |
| HTTP 401/403 | 服务开了鉴权 | 导出 `LIGHTRAG_API_KEY` |
| 状态 `failed` | 解析或抽取失败（模型、embedding、文件损坏） | 把 `原因` 原文给用户，并提示查服务端日志（默认 `lightrag.log`）里同时间的堆栈 |

任何情况下都不要静默失败，也不要把“已排队”说成“已入库”。

## 语言

面向人的文字一律用中文：确认表、入库结果、失败说明、命令行提示，以及后续基于知识库生成的用例与报告。
文件名、路径、字段名（`track_id`、`doc_id`）、原始错误信息和协议名（HTTP、WebUI）保持原样——翻译它们只会让用户对不上日志。

## 规则

1. 入库前必须展示上面的确认表，拿到明确确认后才写。
2. 一次处理一个文件。用户一次给多个文件时，仍然**逐个**展示确认表、逐个确认、逐个入库；不要用一次“都入库”覆盖全部，除非用户明确这么授权。
3. 不要为了“入库成功”去改原文件、删内容或换扩展名——用户给什么就入什么。
4. 文档里如果含密钥、密码、个人身份信息，入库前提醒一句：知识库是明文存储的。
5. 入库成功后再给出下一步建议（检索 / 生成用例 / 生成自动化脚本），不要提前替用户决定。
6. 失败后先上报（步骤 / 原因 / 建议），由用户决定重试还是清理；未确认不得执行 `purge`。
7. 所有写操作留在项目目录内；`repo-src/`、`lightrag/`、`.venv/`、`rag_storage/` 一概不碰。
8. 每个关键步骤都要有日志可查：入库、检索、清理、回补、用户决策，缺一步就等于没做。
9. 缺参数先按上下文补，补不出来就问；缺事实不要编，走 `backfill` 且必须用户确认。
10. 与知识库主题无关的内容**不回补**：上报并说明“知识库不覆盖且与本库主题无关”，是否纳入由用户明确决定。

## 脚本

`scripts/ingest_file.py`，只用标准库 + 可选依赖（tiktoken / pypdf / python-docx）。

```bash
# 只看不写
python ingest_file.py inspect  <file> [--json] [--base-url URL] [--project-dir DIR]

# 写入并等待处理完成（失败默认不清理，先上报）
python ingest_file.py ingest   <file> [--json] [--no-wait] [--timeout 1800] \
                                      [--replace] [--purge-on-failure] [--project-dir DIR]

# 用户确认后，手动清理一篇文档的全部痕迹
python ingest_file.py purge    <file> [--json] [--project-dir DIR]

# 检索（--expect 用来检查图谱缺口）
python ingest_file.py query    "<问题>" [--mode mix] [--expect "实体A,实体B"] [--json]

# 图谱回补（用户确认后）：写一段补充内容或一个补充文件
python ingest_file.py backfill --text "补充内容……" --source gap-fill [--json]
python ingest_file.py backfill <补充文件> --source gap-fill [--json]

# 日志与决策
python ingest_file.py log      [--limit 50] [--json]
python ingest_file.py note     "用户选择：清理 <file>"
```

`--replace` 用于同名冲突：脚本先按 `file_path` 反查真实 id，**在删除前把 `inputs/` 里还留着的旧副本备份到 `inputs/.replace-backup/`**，再删旧文档、确认记录消失、上传新文件。替换是“先删后传”，传失败时旧文档已经没了——所以脚本会打印备份路径；如果连源文件都没留下，失败信息会明说“没有可用副本”。

脚本的其它内建保护：

- **流式上传**：文件按 1 MB 分块发送，内存里只留一块，100 MB 的文件不会把内存打满；
- **试运行时查重**：`inspect` 会按文件名查一次，命中就提示“同名文档已存在（id, 状态），上传会 409”，不必等失败才知道；
- **入库后自检**：对比入库前后的图谱实体集合，输出“新增实体 N（before → after）”；0 新增会被当作可疑信号提示；
- **失败只上报**：默认不清理，输出重试命令与清理命令，由用户选。

`--purge-on-failure` 只给自动化流水线用：加了才会在失败后自动清理。交互场景保持默认，先问用户。

`--json` 输出机器可读结构（`file`、`doc_type`、`estimated_tokens`、`working_dir`、
`doc_id`、`status`、`stage`、`error`、`purge`、`graph`、`has_conflict` 等），适合串进其它脚本；人读场景用默认的表格输出。

退出码：`0` 成功；`1` 入库失败或服务不可用；`2` 输入无效（文件不存在、空文件、后缀不支持）。

## 为什么走 HTTP 而不是在进程里 new 一个 LightRAG

本机默认用 NetworkX 图存储，它声明了单写者：服务进程已经把图缓存在内存里、按整份文件重写。
再起一个进程往同一个 `working_dir` 写，两边会互相覆盖（见仓库的
`docs/design/NetworkXSingleWriterContract.md`，本机已归档到 `repo-src/docs/design/`）。走 HTTP 让正在跑的服务自己完成解析、切分、
抽取和落盘，既避开这个冲突，也自动复用了服务端配置好的解析引擎与 LLM/embedding。
