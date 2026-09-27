"""把项目打成可上传到服务器的 zip（自动排除密钥和本机运行时数据）。

用法：
    python pack.py        # 生成 dist/planagent.zip

包里的 data/config.json 是「空密钥模板」，部署后在网页「设置」里填你自己的密钥，
所以这个包可以放心分享给别人，也可以放进 Git 仓库。
"""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

BASE = Path(__file__).resolve().parent
OUT = BASE / "dist" / "planagent.zip"

SKIP_DIRS = {"__pycache__", ".venv", "venv", "dist", ".git", ".idea", ".vscode", "data"}
SKIP_SUFFIX = {".pyc", ".pyo", ".log", ".zip", ".tmp"}

# 打包时写进 data/config.json 的干净模板：不含任何密钥
SAFE_CONFIG = {
    "deepseek_api_key": "",
    "deepseek_base_url": "https://api.deepseek.com",
    "deepseek_model": "deepseek-flash",
    "thinking_enabled": True,
    "reasoning_effort": "high",
    "wecom_webhook": "",
    "wecom_webhook_enabled": True,
    "notify_enabled": True,
    "catch_up_minutes": 30,
    "host": "0.0.0.0",
    "port": 8765,
    "public_base_url": "",
    "checkin_token_hours": 24,
    "user_name": "同学",
    "access_password": "",
    "checkin_token_secret": "",
}


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    files: list[str] = []
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(BASE.rglob("*")):
            if path.is_dir():
                continue
            rel = path.relative_to(BASE)
            if any(part in SKIP_DIRS for part in rel.parts):
                continue
            if path.suffix in SKIP_SUFFIX:
                continue
            zf.write(path, f"planagent/{rel.as_posix()}")
            files.append(rel.as_posix())
        zf.writestr("planagent/data/config.json", json.dumps(SAFE_CONFIG, ensure_ascii=False, indent=2))
        zf.writestr(
            "planagent/data/.gitkeep",
            "# data/ 里的内容是本机运行时数据（密钥、计划、聊天记录），不要提交到版本库\n",
        )

    size_kb = OUT.stat().st_size / 1024
    print(f"已生成 {OUT}  ({size_kb:.1f} KB, {len(files) + 2} 个文件)")
    for name in files:
        print("  ", name)
    print("\n包内 data/config.json 为空白模板，部署后在网页「设置」里填写密钥即可。")
    print("⚠️ 覆盖部署到已有环境前，先备份服务器上的 data/ 目录，否则会冲掉已填的密钥和计划数据。")


if __name__ == "__main__":
    main()
