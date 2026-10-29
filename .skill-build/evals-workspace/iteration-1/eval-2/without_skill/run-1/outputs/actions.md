pwd; ls -la; ls -la /Users/miguoqing/.agents/skills/lightrag-ingest/evals/files/
curl -s -m 5 http://127.0.0.1:9621/health
file /Users/miguoqing/.agents/skills/lightrag-ingest/evals/files/scan.pdf
head -c 600 /Users/miguoqing/.agents/skills/lightrag-ingest/evals/files/scan.pdf | cat -v
/Users/miguoqing/LightRAG/.venv/bin/python -c "from pypdf import PdfReader; import tiktoken; r=PdfReader('/Users/miguoqing/.agents/skills/lightrag-ingest/evals/files/scan.pdf'); print('pages:',len(r.pages)); [print('page',i+1,'chars:',len(p.extract_text() or ''),'contents:',p.get_contents(),'images:',list(p.images)) for i,p in enumerate(r.pages)]; enc=tiktoken.get_encoding('cl100k_base'); full='\n'.join((p.extract_text() or '') for p in r.pages); print('total chars:',len(full),'tokens:',len(enc.encode(full)))"
curl -s -m 10 http://127.0.0.1:9621/openapi.json | python3 -c 'import sys,json; d=json.load(sys.stdin); [print(p, list(v.keys())) for p,v in d["paths"].items()]'
curl -s -m 10 http://127.0.0.1:9621/openapi.json | python3 -c 'import sys,json; d=json.load(sys.stdin); print(json.dumps(d["paths"]["/documents/upload"],ensure_ascii=False,indent=1))'
curl -s -m 10 -X POST http://127.0.0.1:9621/documents/paginated -H 'Content-Type: application/json' -d '{"page":1,"page_size":20}'
ls -la /Users/miguoqing/LightRAG/inputs /Users/miguoqing/LightRAG/rag_storage
find /Users/miguoqing/LightRAG/inputs/__parsed__ -iname '*scan*' -maxdepth 3
mkdir -p /tmp/lr-scan-parse && cd /Users/miguoqing/LightRAG && .venv/bin/python -m lightrag.parser.cli /Users/miguoqing/.agents/skills/lightrag-ingest/evals/files/scan.pdf --engine legacy -o /tmp/lr-scan-parse --preview 5
cd /Users/miguoqing/LightRAG && .venv/bin/python -m lightrag.parser.cli /Users/miguoqing/.agents/skills/lightrag-ingest/evals/files/scan.pdf --engine native -o /tmp/lr-scan-parse-native --preview 5
curl -s -m 3 -o /dev/null -w 'docling:%{http_code}\n' http://localhost:5001/health
curl -s -m 3 -o /dev/null -w 'mineru:%{http_code}\n' http://127.0.0.1:8000/health
curl -s -m 3 -o /dev/null -w 'ollama:%{http_code}\n' http://localhost:11434/api/tags
/Users/miguoqing/LightRAG/.venv/bin/python -c "from pypdf import PdfReader; r=PdfReader('/Users/miguoqing/.agents/skills/lightrag-ingest/evals/files/scan.pdf'); print(dict(r.metadata or {})); print(len(r.pages), [len(p.extract_text() or '') for p in r.pages])"
mkdir -p /Users/miguoqing/LightRAG/.skill-build/evals-workspace/iteration-1/eval-2/without_skill/outputs
