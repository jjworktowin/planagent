@echo off
chcp 65001 >nul
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo [错误] 没有找到 python，请先安装 Python 3.10+ 并加入 PATH。
  pause
  exit /b 1
)

python -c "import fastapi, uvicorn, openai, requests" 2>nul
if errorlevel 1 (
  echo 正在安装依赖...
  python -m pip install -r requirements.txt
)

python main.py %*
if errorlevel 1 pause
