入库失败：broken.xyz
失败步骤：inspect（试运行阶段被拦下，没有上传）
状态：failed（脚本退出码 2 = 输入无效，不是知识库侧的处理失败）
原因：服务端不接受 .xyz —— 输入无效：服务端不接受 .xyz；可用后缀：.bat, .c, .conf, .cpp, .css, .csv, .docx, .epub, .go, .h, .hpp, .htm, .html, .ini, .java, .js, .json, .less, .log, .md, .mdx, .odt, .pdf, .php, .pptx, .properties, .py, .rb, .rtf, .scss, .sh, .sql, .swift, .tex, .textpack, .ts, .txt, .xlsx, .xml, .yaml, .yml
建议：这个后缀不在服务端允许列表里，硬传只会拿到 HTTP 400。要真正入库，请给我一份 .md / .txt / .pdf 的版本（技能规则不允许我私自改扩展名或转格式）；如果这个文件只是用来测“不支持的格式”这条失败路径，那就到此为止。

清理：已确认无需执行 —— 本次没有产生任何中间数据
　　上传副本：无（inputs/ 下没有 broken.xyz）
　　解析产物：无（inputs/__parsed__/ 仍只有原有的 企业通讯录*.html 与 打卡管理.html）
　　文档记录：无（知识库里没有 broken.xyz；我检查时只有「打卡管理.html」一篇 processed，未被动过。期间并行的其它 eval 运行写入了 sample.md、spec.docx，与本次操作无关）
　　所以我没跑 purge、没删任何东西，也没有为了“入库成功”去改文件名或转格式。

补充说明两点：
1. broken.xyz 本身是 20 字节的 ASCII 文本，内容是 `unsupported fixture`，文件读得到、不为空，问题只在后缀不被接受。
2. 技能默认是“失败先上报、清理等你点头”；你这次说了“失败就把中间数据清掉”，但当前没有任何东西可清，所以不存在要不要自动清的取舍。真要重试，命令是：
     .venv/bin/python /Users/miguoqing/.agents/skills/lightrag-ingest/scripts/ingest_file.py ingest "<换好后缀的副本路径>" --timeout 1800

下一步你可以选：
- 给一份 .md / .txt / .pdf 版本，我重新做试运行并出确认表；
- 或者明确说“授权把 broken.xyz 另存为 broken.txt 副本再入库”，我按副本走全流程（原文件不动，但内容只有一行 `unsupported fixture`，入库价值基本为零）；
- 或者先放着，我什么都不做。
