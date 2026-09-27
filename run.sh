#!/usr/bin/env bash
# Linux 下的启动脚本（宝塔「Python 项目」也可以直接把这条命令填进去）
set -euo pipefail
cd "$(dirname "$0")"

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8765}"

if [ ! -x ".venv/bin/python" ]; then
  echo "[planagent] 初始化虚拟环境..."
  python3 -m venv .venv
  .venv/bin/pip install -U pip
  .venv/bin/pip install -r requirements.txt
fi

exec .venv/bin/python main.py --host "$HOST" --port "$PORT" --no-browser
