入库失败了，`broken.xyz` 没能进入知识库。

**失败原因**
LightRAG 服务端只接收白名单内的扩展名，`.xyz` 不在其中。上传接口 `POST /documents/upload` 直接返回 400：

```
{"detail":"Unsupported file type. Supported types: ('.bat', '.c', '.conf', '.cpp', '.css', '.csv', '.docx', '.epub', '.go', '.h', '.hpp', '.htm', '.html', '.ini', '.java', '.js', '.json', '.less', '.log', '.md', '.mdx', '.odt', '.pdf', '.php', '.pptx', '.properties', '.py', '.rb', '.rtf', '.scss', '.sh', '.sql', '.swift', '.tex', '.textpack', '.ts', '.txt', '.xlsx', '.xml', '.yaml', '.yml')}
```

请求在类型校验阶段就被拒绝，没有进入解析、分块、抽取或写图流程，所以这次是“干净的失败”，没有产生需要清理的中间数据。

**清理情况（已核对，无需清理）**
- 文档记录数：入库前后都是 `processed: 1, failed: 0, all: 1`，没有新增文档，也没有留下 failed 状态记录。
- 暂存区 `inputs/` 目录为空，`inputs/__parsed__/` 里只有以前那批 `.html` 文件，没有 `broken.xyz` 或它的解析产物。
- 在 `rag_storage` 中检索 `broken.xyz` 无任何命中，没有残留的分块、向量或图节点。
- 流水线状态 `busy: false`，无排队任务；此前的 job 是别的文档删除任务，已正常结束。
- 我没有删除任何已有文件，也没有改动 `repo-src`、`lightrag`、`.venv`、`rag_storage` 下的内容。

**如果想要入库，两个办法**
1. 把它按真实内容改名为受支持的扩展名（这段内容是纯文本，改成 `.txt` 或 `.md` 即可），然后重新上传；
2. 或者你确认一下这个文件本身是不是放错了/损坏了，换成正确的源文件再入库。
告诉我选哪种，我再执行。
