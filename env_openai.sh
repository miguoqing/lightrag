#!/usr/bin/env bash
# LightRAG 本地启动脚本
#
# 配置统一放在项目根目录的 .env —— LightRAG 启动时由 lightrag/api/config.py 的
# load_dotenv 自动读取，不依赖登录 shell、终端、IDE 的 Run Configuration。
#
# 这里【不要】再写 export LLM_BINDING_HOST=$DEEPSEEK_* 这类行：
#   1) 当前 shell 里 DEEPSEEK_* 为空时，它会导出一个空串；
#   2) 空串也算"已设置"，会盖掉 .env（python-dotenv override=False /
#      get_env_value 只对 None 兜底）；
#   3) 于是 llm/openai.py 里 api_key 为空，回退去读 OPENAI_API_KEY -> KeyError。
#
# 用法：bash env_openai.sh   或   source env_openai.sh

# 清掉旧终端 / 旧脚本可能残留的空值，让 .env 成为唯一来源
unset LLM_BINDING LLM_MODEL LLM_BINDING_HOST LLM_BINDING_API_KEY
unset EMBEDDING_BINDING EMBEDDING_MODEL EMBEDDING_DIM
unset EMBEDDING_BINDING_HOST EMBEDDING_BINDING_API_KEY

export LOG_LEVEL=DEBUG
export VERBOSE=True

lightrag-server --verbose
