ls -la /Users/miguoqing/.agents/skills/lightrag-ingest/evals/files/
ls -la /Users/miguoqing/.agents/skills/lightrag-ingest/scripts/
ls /Users/miguoqing/.agents/skills/lightrag-ingest/evals/
curl -sS -m 10 http://127.0.0.1:9621/health
ls -la /Users/miguoqing/LightRAG
cat /Users/miguoqing/.agents/skills/lightrag-ingest/evals/evals.json
read /Users/miguoqing/.agents/skills/lightrag-ingest/evals/files/sample.md
/Users/miguoqing/LightRAG/.venv/bin/python -V
/Users/miguoqing/LightRAG/.venv/bin/python -c "import tiktoken, docx; print('tiktoken+docx ok')"
/Users/miguoqing/LightRAG/.venv/bin/python /Users/miguoqing/.agents/skills/lightrag-ingest/scripts/ingest_file.py inspect /Users/miguoqing/.agents/skills/lightrag-ingest/evals/files/sample.md --base-url http://127.0.0.1:9621 --project-dir /Users/miguoqing/LightRAG   # 参数顺序错误，argparse 退出码 2，未执行
/Users/miguoqing/LightRAG/.venv/bin/python /Users/miguoqing/.agents/skills/lightrag-ingest/scripts/ingest_file.py inspect /Users/miguoqing/.agents/skills/lightrag-ingest/evals/files/spec.docx --base-url http://127.0.0.1:9621 --project-dir /Users/miguoqing/LightRAG   # 参数顺序错误，argparse 退出码 2，未执行
/Users/miguoqing/LightRAG/.venv/bin/python /Users/miguoqing/.agents/skills/lightrag-ingest/scripts/ingest_file.py inspect /Users/miguoqing/.agents/skills/lightrag-ingest/evals/files/sample.md   # 使用默认 --base-url http://127.0.0.1:9621 --project-dir /Users/miguoqing/LightRAG，只读试运行
/Users/miguoqing/LightRAG/.venv/bin/python /Users/miguoqing/.agents/skills/lightrag-ingest/scripts/ingest_file.py inspect /Users/miguoqing/.agents/skills/lightrag-ingest/evals/files/spec.docx   # 使用默认 --base-url http://127.0.0.1:9621 --project-dir /Users/miguoqing/LightRAG，只读试运行
/Users/miguoqing/LightRAG/.venv/bin/python - <<'EOF'   # 用 python-docx 只读抽取 spec.docx 段落，确认正文 4 段、无表格无图片
EOF
curl -sS -m 10 "http://127.0.0.1:9621/documents"   # 405 Method Not Allowed，未取得列表
curl -sS -m 10 "http://127.0.0.1:9621/documents/supported_file_types"
curl -sS -m 10 -X POST "http://127.0.0.1:9621/documents/paginated" -H 'Content-Type: application/json' -d '{"page":1,"page_size":20}'   # 只读查询现有文档记录
ls -la /Users/miguoqing/LightRAG/inputs /Users/miguoqing/LightRAG/inputs/__parsed__
mkdir -p /Users/miguoqing/LightRAG/.skill-build/evals-workspace/iteration-1/eval-3/with_skill/outputs/
write /Users/miguoqing/LightRAG/.skill-build/evals-workspace/iteration-1/eval-3/with_skill/outputs/response.md
write /Users/miguoqing/LightRAG/.skill-build/evals-workspace/iteration-1/eval-3/with_skill/outputs/actions.md
