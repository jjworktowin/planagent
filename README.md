# 计划智能体 · PlanAgent

一个基于 **DeepSeek 思考模式** 的本地计划助手：和智能体聊几句，它就把你的目标拆成一张能坚持的计划表，
到点通过**企业微信机器人**推送提醒，消息里带**一键打卡链接**，签到采用「续火花」机制。

## 快速开始

```powershell
cd D:\planagent
python -m pip install -r requirements.txt
python main.py            # 或双击 run.bat
```

首次启动后打开 `http://127.0.0.1:8765` → 左侧「设置」，填两个东西就能用起来：

- **DeepSeek API 密钥**（必填，[在这里申请](https://platform.deepseek.com/api_keys)）
- **企业微信机器人 Webhook**（想要到点推送提醒就填）

也可以改用环境变量注入，不写进任何文件：

```powershell
$env:DEEPSEEK_API_KEY="sk-你的密钥"
$env:WECOM_WEBHOOK="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=你的key"
python main.py
```

启动后浏览器自动打开 `http://127.0.0.1:8765`。手机访问用局域网地址（启动时控制台会打印），
例如 `http://192.168.1.8:8765`。

## 三大功能

### 1. 对话生成计划表
在「智能对话」里说清 **目标 / 天数 / 每天做什么 / 几点提醒**，智能体会先问清缺失信息，
再调用工具生成计划并保存。所有计划统一存放在 **一个文件**：`data/plans.json`。

### 2. 查看与修改计划
左侧「我的计划」点开任意计划，可以改标题、开始日期、总天数、提醒时间、每天的任务，
也能暂停、恢复、删除，或直接「立即推送提醒」「复制打卡链接」。

### 3. 打卡（仿续火花）
到点后企业微信收到提醒文本 + 打卡链接，点开链接即签到成功：

- 昨天打过卡、今天再打 → 连续天数 +1，火花更旺 🔥
- 中间断了 → 火花熄灭，连续天数从 1 重新点燃，并记录断签次数
- 同一天重复点 → 只提示「今天已经打过卡啦」，不会重复计数

### 4. 配置页
「设置」里可以配置 **DeepSeek 密钥 / 模型 / 思考强度**、**企业微信机器人 Webhook**、
**通知总开关**、补发窗口、打卡链接有效期、对外访问地址。

## 目录结构

```
D:\planagent
├─ main.py              启动入口（uvicorn）
├─ run.bat              Windows 一键启动
├─ requirements.txt
├─ app\
│  ├─ config.py         配置存储（data/config.json）
│  ├─ store.py          计划存储 + 打卡续火花逻辑（data/plans.json）
│  ├─ agent.py          DeepSeek 智能体（思考模式 + 工具调用）
│  ├─ checkin.py        打卡链接签名 / 校验 / 提醒文案
│  ├─ notifier.py       企业微信机器人推送
│  ├─ scheduler.py      后台每 20 秒扫描，到点推送
│  └─ server.py         FastAPI 路由
├─ static\              网页界面（对话 / 我的计划 / 设置）
└─ data\                运行时数据（配置、计划、状态、会话）
```

## 关于 DeepSeek 思考模式

按官方文档实现（https://api-docs.deepseek.com/zh-cn/guides/thinking_mode ）：

| 项目 | 实现方式 |
| --- | --- |
| 接口地址 | `https://api.deepseek.com`（OpenAI 兼容） |
| 思考开关 | `extra_body={"thinking": {"type": "enabled" / "disabled"}}` |
| 思考强度 | `reasoning_effort` = `low` / `high` / `max`（`medium` 实际映射为 `high`） |
| 思维链 | 从 `message.reasoning_content` 读取，界面上可展开「思考过程」 |
| 工具调用 | 携带 `tools` 时，历史轮次的 `reasoning_content` 会完整回传，避免 400 报错 |
| 注意 | 思考模式下 `temperature`、`presence_penalty`、`frequency_penalty` 不生效，因此未使用 |

## 手机打卡需要能访问到电脑

打卡链接默认使用电脑的局域网 IP。如果手机和电脑不在同一个网络，
请在「设置 → 打卡链接使用的外网/局域网地址」里填写内网穿透地址（如 `https://xxx.trycloudflare.com`）。

## 数据安全

**代码里不含任何密钥。** DeepSeek 密钥、企业微信 Webhook 都只保存在本机 `data/config.json`，
也可以在服务器上用环境变量 `DEEPSEEK_API_KEY` / `WECOM_WEBHOOK` 注入。

`data/` 目录已经被 `.gitignore` 排除，里面有：

| 文件 | 内容 |
| --- | --- |
| `config.json` | 密钥、机器人地址、打卡地址、访问口令 |
| `plans.json` | 你的所有计划与打卡记录 |
| `sessions.json` | 对话历史 |
| `state.json` | 提醒推送去重记录 |

所以克隆这个仓库的人拿到的是干净的代码，不会有你的任何数据和密钥。

### 要发布到 GitHub / 分享给别人

发布前自查一遍（确保没有把自己本机的配置打包进去）：

```bash
git status --short          # data/ 和 dist/ 不应该出现在待提交列表里
git grep -nE "sk-[A-Za-z0-9]{20,}|webhook/send\?key=" -- . ':!data'   # 应该没有任何输出
```

如果把整个文件夹压缩发人，记得先删掉 `data/` 里的内容（至少 `config.json`）。

### 密钥一旦泄露怎么办

只要密钥曾经出现在聊天记录、截图、压缩包或公开仓库里，就当作已泄露：

- DeepSeek 密钥 → 到控制台**删除旧密钥、重新生成**
- 企业微信机器人 Webhook → 在企业微信群里**移除旧机器人、重新添加**，拿到新地址

换完在网页「设置」里重新填一次即可，旧密钥立刻失效。
