ls -la /Users/miguoqing/.agents/skills/lightrag-ingest/evals/files/
file /Users/miguoqing/.agents/skills/lightrag-ingest/evals/files/broken.xyz
wc -c /Users/miguoqing/.agents/skills/lightrag-ingest/evals/files/broken.xyz
head -c 500 /Users/miguoqing/.agents/skills/lightrag-ingest/evals/files/broken.xyz | od -c | head -20
curl -s -m 5 http://127.0.0.1:9621/health
curl -s -m 5 http://127.0.0.1:9621/documents/supported_file_types
ls -la /Users/miguoqing/LightRAG/inputs/
ls -la /Users/miguoqing/LightRAG/scripts/
cd /Users/miguoqing/LightRAG && /Users/miguoqing/LightRAG/.venv/bin/python /Users/miguoqing/.agents/skills/lightrag-ingest/scripts/ingest_file.py inspect /Users/miguoqing/.agents/skills/lightrag-ingest/evals/files/broken.xyz   # EXIT=2, 输入无效：服务端不接受 .xyz
curl -s -m 10 -X POST http://127.0.0.1:9621/documents/paginated -H 'Content-Type: application/json' -d '{"page":1,"page_size":200}'
cd /Users/miguoqing/LightRAG && find inputs -maxdepth 2
cd /Users/miguoqing/LightRAG && find inputs -name '*broken*' -o -name '*.xyz'
mkdir -p "/Users/miguoqing/LightRAG/.skill-build/evals-workspace/iteration-1/eval-4/with_skill/outputs"
