"""计划智能体 · 启动入口

用法：
    python main.py                 # 默认 0.0.0.0:8765，并自动打开浏览器
    python main.py --port 9000     # 换端口
    python main.py --no-browser    # 不自动打开浏览器
"""

from __future__ import annotations

import argparse
import threading
import time
import webbrowser

import uvicorn

from app import paths
from app.config import ConfigStore
from app.server import create_app


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="计划智能体 PlanAgent")
    parser.add_argument("--host", default=None, help="监听地址，默认 0.0.0.0（手机可访问）")
    parser.add_argument("--port", type=int, default=None, help="监听端口，默认 8765")
    parser.add_argument("--no-browser", action="store_true", help="启动后不自动打开浏览器")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths.ensure_dirs()
    config = ConfigStore()

    host = args.host or config.get("host", "0.0.0.0")
    port = args.port or config.get_int("port", 8765)
    if args.host or args.port:
        config.update({"host": host, "port": port})

    app = create_app(config)
    lan_url = f"http://{paths.get_lan_ip()}:{port}"

    print("=" * 62)
    print("  计划智能体 PlanAgent")
    print(f"  本机访问：http://127.0.0.1:{port}")
    print(f"  手机访问（同一 WiFi）：{lan_url}")
    print(f"  发送给企业微信的打卡链接会使用：{config.effective_base_url()}/checkin")
    print(f"  DeepSeek 密钥：{'已配置' if config.deepseek_ready() else '未配置（请到左侧设置里填写）'}")
    print(f"  企业微信提醒：{'已开启' if config.notify_ready() else '未就绪（未开启或未配置地址）'}")
    print("  按 Ctrl+C 停止服务")
    print("=" * 62)

    if not args.no_browser:
        def _open() -> None:
            time.sleep(1.5)
            try:
                webbrowser.open(f"http://127.0.0.1:{port}")
            except Exception:  # noqa: BLE001
                pass

        threading.Thread(target=_open, daemon=True).start()

    uvicorn.run(app, host=host, port=port, log_level="info", access_log=False)


if __name__ == "__main__":
    main()
