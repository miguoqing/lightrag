ls -la /Users/miguoqing/.agents/skills/lightrag-ingest/evals/files/scan.pdf
file /Users/miguoqing/.agents/skills/lightrag-ingest/evals/files/scan.pdf
ls /Users/miguoqing/.agents/skills/lightrag-ingest/scripts/
curl -s -m 5 http://127.0.0.1:9621/health
curl -s -m 5 http://127.0.0.1:9621/documents/supported_file_types
cd /Users/miguoqing/LightRAG && PY="${LIGHTRAG_PYTHON:-/Users/miguoqing/LightRAG/.venv/bin/python}"; [ -x "$PY" ] || PY=python3; "$PY" /Users/miguoqing/.agents/skills/lightrag-ingest/scripts/ingest_file.py inspect /Users/miguoqing/.agents/skills/lightrag-ingest/evals/files/scan.pdf
mkdir -p /Users/miguoqing/LightRAG/.skill-build/evals-workspace/iteration-1/eval-2/with_skill/outputs
