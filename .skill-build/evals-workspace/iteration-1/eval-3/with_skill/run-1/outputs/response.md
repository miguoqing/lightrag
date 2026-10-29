已对两个文件做完**只读试运行**，**还没有写入任何数据**。按技能规则，多文件会**逐个确认、逐个入库**——你确认后我会先入 sample.md，再入 spec.docx，不会一次性全写。

⚠ 需要你注意：这两个文件在知识库里**已存在同名且已处理（processed）的文档**，直接上传会返回 HTTP 409，因此入库需要加 `--replace`（先删旧记录再上传；旧副本会先备份到 `inputs/.replace-backup/`）。

【1/2】sample.md
```text
文件：sample.md
文档类型：text
来源：/Users/miguoqing/.agents/skills/lightrag-ingest/evals/files/sample.md（本地文件）
大小：415 B
预估 token：≈ 158（tiktoken / cl100k_base，正文 159 字符）
同名记录：doc-7cce010dc015a937e6841b4e289c7b7d（processed）→ 需 --replace
目标知识库：/Users/miguoqing/LightRAG/rag_storage
```

【2/2】spec.docx
```text
文件：spec.docx
文档类型：document
来源：/Users/miguoqing/.agents/skills/lightrag-ingest/evals/files/spec.docx（本地文件）
大小：35.9 KB
预估 token：≈ 73（tiktoken / cl100k_base，正文 75 字符；docx 内只有 4 段文本，无表格、无图片）
同名记录：doc-892fa9f21a407156eea354048abf4879（processed）→ 需 --replace
目标知识库：/Users/miguoqing/LightRAG/rag_storage
```

**确认入库吗？** 请分别确认：
- 「两个都确认」→ 我依次用 `--replace` 入库 sample.md，再入库 spec.docx；
- 或只确认其中一个，我先处理那一个。

在你明确回复前，我不会上传、替换或删除任何数据。
