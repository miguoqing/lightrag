ls -l /Users/miguoqing/.agents/skills/lightrag-ingest/evals/files/broken.xyz
file /Users/miguoqing/.agents/skills/lightrag-ingest/evals/files/broken.xyz
curl -s -m 5 http://127.0.0.1:9621/health
curl -s -m 10 'http://127.0.0.1:9621/documents?limit=100'
curl -s -m 10 http://127.0.0.1:9621/openapi.json
curl -s -m 10 http://127.0.0.1:9621/documents/supported_file_types
curl -s -m 10 http://127.0.0.1:9621/documents/status_counts
curl -s -m 10 -X POST http://127.0.0.1:9621/documents/paginated -H 'Content-Type: application/json' -d '{"page":1,"page_size":50}'
curl -s -m 10 http://127.0.0.1:9621/documents/pipeline_status
xxd /Users/miguoqing/.agents/skills/lightrag-ingest/evals/files/broken.xyz
curl -s -m 60 -w '\nHTTP_STATUS:%{http_code}\n' -X POST http://127.0.0.1:9621/documents/upload -F 'file=@/Users/miguoqing/.agents/skills/lightrag-ingest/evals/files/broken.xyz'
ls -la inputs
ls -la inputs/__parsed__
grep -rIl 'broken\.xyz' rag_storage
mkdir -p /Users/miguoqing/LightRAG/.skill-build/evals-workspace/iteration-1/eval-4/without_skill/outputs/
