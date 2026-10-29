ls -la /Users/miguoqing/.agents/skills/lightrag-ingest/evals/files/sample.md
wc -c -l /Users/miguoqing/.agents/skills/lightrag-ingest/evals/files/sample.md
curl -s -m 10 http://127.0.0.1:9621/health
curl -s -m 10 http://127.0.0.1:9621/api/health
curl -s -m 15 http://127.0.0.1:9621/openapi.json -o /tmp/openapi.json
curl -s -m 10 http://127.0.0.1:9621/documents
curl -s -m 10 'http://127.0.0.1:9621/documents?limit=5'
curl -s -m 15 -X POST http://127.0.0.1:9621/documents/paginated -H 'Content-Type: application/json' -d '{"page":1,"page_size":20,"sort_field":"updated_at","sort_direction":"desc"}'
curl -s -m 15 http://127.0.0.1:9621/documents/status_counts
ls -la /Users/miguoqing/LightRAG/inputs
ls -la /Users/miguoqing/LightRAG/inputs/__parsed__/
shasum -a 256 /Users/miguoqing/LightRAG/inputs/__parsed__/sample.md /Users/miguoqing/.agents/skills/lightrag-ingest/evals/files/sample.md
head -c 600 /Users/miguoqing/LightRAG/inputs/__parsed__/sample.md.parsed/sample.blocks.jsonl
python3 -c "t=open('/Users/miguoqing/.agents/skills/lightrag-ingest/evals/files/sample.md',encoding='utf-8').read(); print(len(t), sum(1 for c in t if '\u4e00'<=c<='\u9fff'))"
grep -c "U 盘\|智能考勤机" /Users/miguoqing/LightRAG/inputs/__parsed__/打卡管理.html
grep -o "外出打卡" /Users/miguoqing/LightRAG/inputs/__parsed__/打卡管理.html | wc -l
python3 -c "import json;d=json.load(open('/tmp/openapi.json'));[print(p, ','.join(sorted(o))) for p,o in sorted(d['paths'].items())]"
find /Users/miguoqing/LightRAG/lightrag -maxdepth 4 -name "document_routes.py"
grep -n "canonical\|input_dir" /Users/miguoqing/LightRAG/lightrag/api/routers/document_routes.py | head -40
sed -n 5300,5420p /Users/miguoqing/LightRAG/lightrag/api/routers/document_routes.py
sed -n 5695,5830p /Users/miguoqing/LightRAG/lightrag/api/routers/document_routes.py
curl -s -m 10 -X POST http://127.0.0.1:9621/documents/paginated -H 'Content-Type: application/json' -d '{"page":1,"page_size":10}'
curl -s -m 15 http://127.0.0.1:9621/documents/track_status/upload_20261029_135739_47e25e57
curl -s -m 15 'http://127.0.0.1:9621/graph/label/popular?limit=10'
date
mkdir -p /Users/miguoqing/LightRAG/.skill-build/evals-workspace/iteration-1/eval-1/without_skill/outputs/
