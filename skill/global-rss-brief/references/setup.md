# 部署指南

## 1. Python 环境

需要 Python ≥ 3.10，安装依赖：

```bash
pip install feedparser pyyaml python-docx fastapi uvicorn
```

Windows 上用 `py -m pip install ...` 亦可。macOS/Linux 注意系统 Python 可能受限，建议 `python3 -m venv .venv && source .venv/bin/activate`。

## 2. 代理（必需）

约一半信源在境外，必须配置 HTTP 代理。运行抓取前设置：

```bash
# macOS/Linux
export HTTPS_PROXY=http://127.0.0.1:7890 HTTP_PROXY=http://127.0.0.1:7890 NO_PROXY=127.0.0.1,localhost
# Windows PowerShell
$env:HTTPS_PROXY="http://127.0.0.1:7890"; $env:HTTP_PROXY="http://127.0.0.1:7890"; $env:NO_PROXY="127.0.0.1,localhost"
```

端口按用户实际代理软件调整（Clash 默认 7890，v2ray 常见 10809）。**必须设 NO_PROXY**，否则本机 RSSHub 的请求会被代理劫走。

## 3. RSSHub（覆盖约一半信源，强烈建议）

需要 Node.js ≥ 20（Windows 从 nodejs.org 下载 LTS 安装包即可）：

```bash
git clone --depth 1 https://github.com/DIYgod/RSSHub.git rsshub
cd rsshub && corepack enable && pnpm install && pnpm build
# 启动（常驻）：
NODE_ENV=production PORT=1200 PROXY_URI=http://127.0.0.1:7890 node dist/index.mjs
```

验证：`curl http://127.0.0.1:1200/` 返回 200。

不配 RSSHub 也能跑：`sources.yaml` 里 `via: rsshub` 的源会失败，可用 `python scripts/fetch.py native` 只跑原生 RSS 源（约 100+ 个）。

## 4. 目录结构（技能解压后）

```
<skill-root>/
├── SKILL.md
├── scripts/    fetch.py scheduler.py filter.py generate.py
├── config/     sources.yaml source_names.yaml filter_rules.yaml
├── app/        Web 控制台（React+Vite）
├── server.py   控制台后端（FastAPI，端口 8600）
├── state/      运行状态（自动创建）
└── output/     抓取与简报产出（自动创建）
```

脚本内部用 `Path(__file__).parent` 定位根目录，跨平台安全；但 `config/` 下的清单默认按技能根目录读取——把 `config/*.yaml` 复制到技能根目录，或在根目录建符号链接。推荐复制，便于用户直接改。

## 5. Windows 注意事项

- 调度器常驻：`python scripts/scheduler.py`，可用「任务计划程序」设开机自启（操作：`python.exe`，参数为脚本绝对路径，起始于技能根目录）
- Web 控制台：`npm install` 需要 Node 环境；后端 `uvicorn server:app --port 8600`
- 路径含中文/空格没问题，脚本均未做平台特定假设
- RSSHub 在 Windows 直跑即可，无需 Docker

## 6. 冒烟测试

```bash
python scripts/fetch.py native   # 只跑原生源，应输出 entries_*.jsonl 与报告
python scripts/filter.py         # 筛选最新批次
```

成功率参考：有代理 + RSSHub 时约 124/220 有即时内容，74 静默（正常），≤25 真失败。
