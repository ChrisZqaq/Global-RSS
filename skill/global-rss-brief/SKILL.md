---
name: global-rss-brief
description: 全球资讯 RSS 简报流水线：220 个去重后的全球财经/科技/中国议题信源（原生 RSS + RSSHub 转制），分级定时抓取、增量去重、规则筛选（中国/科技/经济主题，排除政军与快讯短讯）、人工校正学习，最终生成中文 docx 简报。当用户要求「跑资讯简报」「抓取 RSS」「生成简报」「管理信源」「复盘筛选规则」，或提到本技能的信源/简报/筛选词表时使用。也用于首次部署：安装依赖、配置代理、启动调度器与 Web 控制台。
---

# 全球资讯简报（Global RSS Brief）

流水线：`scheduler.py`（分级轮询抓取）→ `filter.py`（规则筛选）→ Agent 翻译总结 → `generate.py`（docx 简报）。

## 首次部署

按 [references/setup.md](references/setup.md) 执行：Python 依赖、代理、RSSHub（可选但覆盖一半信源）、Windows 注意事项。部署后把工作目录设为技能解压目录（所有脚本用相对路径，须在此目录下运行）。

## 日常运行

### 启动采集（常驻）

```bash
export HTTPS_PROXY=http://127.0.0.1:7890 HTTP_PROXY=http://127.0.0.1:7890   # 端口按实际代理改
python scripts/scheduler.py
```

- 分级间隔：fast 源 60s / normal 300s / slow 900s；ETag/Last-Modified 条件请求；失败源 3 倍退避
- RSSHub 源需先启动本地实例（见 setup.md）；无 RSSHub 时 `python scripts/fetch.py native` 只跑原生源
- 状态文件：`state/seen.json`（去重）、`state/poll_state.json`（轮询）、`state/overrides*.json*`（人工标记）
- 产出：`output/entries_*.jsonl`（新条目）、`output/filtered_*.jsonl`（入选条目）、`output/fetch_report_*.json`（信源健康）

### 生成简报（用户要简报时）

1. 找到最新的 `output/filtered_*.jsonl`（或与用户指定时段对应的多份合并去重，按 `link` 去重）
2. 按 [references/brief-format.md](references/brief-format.md) 逐条翻译标题 + 写中文总结段落，产出 `output/brief_content.json`
3. `python scripts/generate.py output/brief_content.json` 生成 docx
4. 条目多时分批处理，单条翻译失败保留原标题并标记，不阻塞整份简报

### Web 控制台（用户要管理信源/人工校正时）

```bash
pip install fastapi uvicorn   # 如未装
python server.py 或 uvicorn server:app --port 8600   # server.py 位于技能根目录
cd app && npm install && npm run dev   # 控制台 http://localhost:7100
```

功能：信源查看/新增/启停（中文名+健康状态），条目浏览（12h 窗口、标签筛选、时间倒序），人工反转（可填理由，写入 `state/overrides.json` 与 `overrides_log.jsonl`）。

### 每周复盘（用户说「复盘筛选」或定期任务触发时）

按 [references/weekly-review.md](references/weekly-review.md)：读 `state/overrides_log.jsonl` 的人工动作与理由，归纳规律，输出 `config/filter_rules.yaml` 的修改 diff 给用户确认，**确认后才写回**。

## 关键规则

- 筛选规则全部在 `config/filter_rules.yaml`，改规则只改 YAML，不改 `filter.py`
- 只保留 12 小时内条目；增量去重以 link 为键
- 境外源必须走代理；RSSHub 地址是本机（127.0.0.1:1200），不是错误
- 静默 ≠ 失败：源可达但 12h 无更新是正常现象
