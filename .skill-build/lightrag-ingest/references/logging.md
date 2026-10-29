# 操作日志与异常处理设计

本文件说明 `lightrag-ingest` 为什么这样记日志、错误怎么分类、用户决策怎么落地。
SKILL.md 只写“怎么做”，这里写“为什么”和字段契约。

## 1. 目标

一条链路从用户上传文件开始，到入库、检索、缺口回补结束。每一步都要能回答三个问题：

1. 做了什么（step/action）；
2. 结果如何（status/detail）；
3. 出错时建议是什么、用户最后怎么决定的（error/suggestion + decision）。

## 2. 事件模型

日志文件：`<project>/.lightrag-ingest/logs/ops-YYYYMMDD.jsonl`，一行一个 JSON 事件。

| 字段 | 必填 | 说明 |
|---|---|---|
| `ts` | 是 | 本地时区 ISO8601，精确到秒 |
| `run_id` | 是 | 一次命令执行一个；格式 `YYYYMMDD-HHMMSS-六位随机` |
| `command` | 是 | `inspect` / `ingest` / `purge` / `query` / `backfill` / `log` / `note` |
| `step` | 是 | 见下表 |
| `action` | 是 | 步骤内的动作，见下表 |
| `status` | 是 | `ok` / `warn` / `fail` |
| `detail` | 否 | 结构化上下文（文件名、token 数、track_id、实体数…） |
| `error` | 否 | 原始错误文本（已脱敏） |
| `suggestion` | 否 | 给用户的修复建议 |
| `duration_ms` | 是 | 从进程启动到该事件的毫秒数 |

步骤与动作：

| step | action | 触发点 |
|---|---|---|
| `cli` | `start` / `end` / `fail` | 命令入口与兜底异常 |
| `inspect` | `done` | 试运行完成（含查重结果） |
| `ingest` | `upload_start` / `upload_ok` / `upload_fail` / `conflict` / `replace_fail` / `wait_done` / `verify` | 上传、等待、图谱自检 |
| `purge` | `lookup` / `done` / `fail` | 清理 |
| `query` | `done` | 检索与缺口检查 |
| `backfill` | `start` / `done` | 知识回补 |
| `decision` | `note` | 用户决策或人工批注 |

## 3. 错误分类

分类在 `classify_error()` 里做，同一类错误永远得到同一句建议，避免每次输出措辞不同。

| category | 触发条件 | 建议 |
|---|---|---|
| `input_missing` | 文件不存在/为空/不是普通文件 | 确认路径与落盘位置 |
| `input_invalid` | 无扩展名等其他输入问题 | 检查参数 |
| `unsupported_type` | 后缀不在服务端白名单 | 转 .md/.txt/.pdf 或换解析引擎 |
| `auth` | HTTP 401/403 | 导出 `LIGHTRAG_API_KEY` |
| `duplicate` | HTTP 409 | `--replace` 或改名 |
| `too_large` | HTTP 413 | 拆分或调大上限 |
| `bad_request` | HTTP 400 | 核对类型与服务端配置 |
| `server_unreachable` | 连接被拒 | 启动服务或用 `--base-url` |
| `timeout` | 请求/等待超时 | 加 `--timeout` 重试 |
| `parse_empty` | 解析不出可用文本 | OCR 或换 docling/mineru |
| `unknown` | 其它 | 查服务端日志堆栈 |

## 4. 决策协议

失败时脚本只上报，不替用户做决定：

1. 输出失败步骤、状态、原因原文、建议；
2. 同时给出“重试”和“清理”两组命令；
3. 用户选择后执行对应命令；
4. 用 `note` 把决策写进日志，形成“失败 → 决策 → 动作”的闭环。

清理本身不做二次判断：是否该清由用户决定，脚本只保证清理动作完整（反查 id → 删除 → 轮询确认 → 清残留）。

## 5. 缺参补齐

| 缺失内容 | 处理 |
|---|---|
| 文件路径 | 先看对话附件与 `inputs/` 里的落盘文件；有唯一候选就直接用并注明来源 |
| 文档类型 | 按后缀推断；`auto` 交给服务端 |
| 问题范围/实体 | 从用户问题里抽取；抽不出就问 |
| 正文/事实 | **不得推断**：向用户要，或走 `backfill` |

原则：**参数可以推断，事实不可以编造。**

## 6. 图谱缺口与回补

判定：`query --expect "A,B"` 对每个实体调用 `GET /graph/label/search`，无匹配即视为缺口。
这只是启发式——实体可能是同义词/别名，所以发现缺口后先换说法或 `--mode naive` 复核一次，再上报。

回补：`backfill --text` / `backfill <file>` 走 `POST /documents/text`，文档来源标记为
`<source>-<时间戳>`，与普通入库走同一条解析/抽取流水线；完成后重新查询验证，并记一条 `note`。

## 7. 失败模式与取舍

- **日志写不进去**（磁盘满、权限不足）：降级为 stderr 提示一次，主流程继续。日志是观测手段，不能成为新的故障点。
- **多进程并发**：`run_id` 随机后缀避免碰撞；同一秒的多个 run 靠它区分。
- **脱敏**：`sk-…` 与 `Bearer …` 在落盘前替换；不做全字段加密——日志要能被 grep。
- **保留策略**：按天分文件，不自动删除。需要归档时由用户决定，脚本不清理历史日志。
