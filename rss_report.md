# 全球政治 / 经济 / 军事新闻 RSS 信源调研与书签覆盖报告

> 数据基准：书签文件 1153 条链接、560 个去重域名；RSSHub 官方路由库（1967 个命名空间，2026-10-12 master）；对全部 560 个域名逐一做了原生 RSS 自动探测。

## 一、总结论

| 口径 | 数量 | 说明 |
|---|---|---|
| 书签总链接 | 1153 | 其中约 130 条是 Google 搜索页，非真正信源 |
| 去重域名 | 560 | |
| **可直接订阅原生 RSS** | **162 个域名** | 探测到 `<link rel="alternate">` 或常见 /feed、/rss 路径 |
| **RSSHub 开源路由可覆盖** | **95 个域名** | 含 71 个没有原生 RSS、只能靠 RSSHub 的 |
| 两者都支持 | 24 | 如 SCMP、Foreign Affairs、Brookings、CFR |
| **合计可覆盖** | **233 个域名（41.6%）** | 对应 521 条书签（占真实信源链接约 51%） |
| 暂无开源 RSS 覆盖 | 327 个域名 | 多为咨询报告库、智库 PDF 库、工具站、公众号文章页 |

一句话：**书签里真正的"新闻媒体"信源几乎 100% 可被 RSS（原生或 RSSHub）覆盖；覆盖不了的主要不是新闻站，而是报告下载页、搜索页和工具站，这些本来就不适合 RSS 订阅。**

## 二、推荐的核心免费信源清单（政治 / 经济 / 军事，已去重）

### 1. 综合通讯社与大报（免费 RSS 直接订阅）

| 信源 | RSS 地址 | 覆盖 |
|---|---|---|
| AP 美联社 | apnews.com（RSSHub `/apnews/topics`） | RSSHub |
| Reuters 路透 | reuters.com（RSSHub `/reuters/...`） | RSSHub（原生 RSS 已于 2020 年关闭） |
| BBC | bbc.com（RSSHub `/bbc/:channel?`） | RSSHub |
| The Guardian | theguardian.com（RSSHub `/theguardian/:edition/:category?`） | RSSHub |
| DW 德国之声 | dw.com（RSSHub `/dw/...`） | RSSHub |
| VOA 中文 | voachinese.com（RSSHub `/voa/...`） | RSSHub |
| RFI | rfi.fr | RSSHub |
| TASS 塔斯社 | tass.com | RSSHub |
| Al Jazeera | aljazeera.com | RSSHub |
| ABC 澳洲 | abc.net.au | RSSHub |

### 2. 财经媒体（书签中高频）

| 信源 | 方式 | 备注 |
|---|---|---|
| Bloomberg | RSSHub `/bloomberg/...` | 付费墙，RSS 只有摘要 |
| FT 中文网 | RSSHub `/ft/chinese/...` | ftchinese.com |
| WSJ 中文 | RSSHub `/wsj/...`（cn.wsj.com） | |
| Nikkei Asia / 日经中文 | RSSHub `/nikkei/...` | |
| SCMP 南华早报 | 原生 `https://www.scmp.com/rss/feed` + RSSHub | |
| Fortune | 原生 `https://fortune.com/feed` | |
| ZeroHedge | 原生（RSSHub 也可） | |
| Cryptopolitan | 原生 `https://www.cryptopolitan.com/feed/` | 简报样例的信源 |
| OilPrice | 原生 `https://oilprice.com/rss.xml` | 能源 |
| 华尔街见闻 / 新浪财经 / 观察者网 / 环球网 / 参考消息 | RSSHub（wallstreetcn / sina / guancha / huanqiu / cankaoxiaoxi） | 中文 |
| 联合早报 | RSSHub `/zaobao/...` | |
| 端传媒 | 原生 `https://theinitium.com/rss/` | |
| 香港01 | RSSHub `/hk01/...` | |

### 3. 智库 / 研究机构（政治、军事、地缘，书签高频且几乎全有原生 RSS）

| 信源 | RSS |
|---|---|
| Atlantic Council 大西洋理事会 | `https://www.atlanticcouncil.org/feed/` |
| CSIS | `https://csis.org/rss.xml` |
| CFR 外交关系委员会 | `https://cfr.org/feed` |
| Brookings 布鲁金斯 | `https://www.brookings.edu/feed/` |
| Carnegie 卡内基 | RSSHub `/carnegieendowment/...` |
| Foreign Affairs | `https://www.foreignaffairs.com/rss.xml` |
| Foreign Policy | `https://foreignpolicy.com/feed` |
| National Interest | `https://nationalinterest.org/feed` |
| War on the Rocks（军事） | `https://warontherocks.com/feed` |
| ASPI Strategist（澳，军事） | `https://aspistrategist.org.au/feed` |
| Geopolitical Monitor | `https://geopoliticalmonitor.com/feed` |
| Lowy Institute | `https://lowyinstitute.org/feed` |
| SWP（德） | `https://swp-berlin.org/rss.xml` |
| MERICS（中国研究） | `https://merics.org/rss` |
| GMF / AEI / Hudson / Hoover / Cato | 均有原生 RSS |
| Project Syndicate | `https://project-syndicate.org/rss` |
| Bruegel（欧洲经济） | `https://bruegel.org/rss.xml` |
| PIIE / OMFIF / Rhodium | 原生 RSS |

### 4. 国际组织 / 官方

| 信源 | 方式 |
|---|---|
| IMF / WTO / 白宫 | RSSHub（`/imf/...`、`/wto/...`、`/whitehouse/...`） |
| Federal Reserve | 原生 `https://www.federalreserve.gov/feeds/feeds.xml` |
| NBER | RSSHub `/nber/papers` |

### 5. RSSHub 可补充的顶级源（书签没有但强烈建议加）

- `/reuters/theWire` — 路透快讯（经济军事政治首选）
- `/apnews/topics/:topic` — apf-top-news / politics / business
- `/bbc/world`、`/bbc/chinese`
- `/theguardian/world`、`/theguardian/business`
- `/aljazeera/news`
- `/kyodonews/...`（共同社，有中文网 china.kyodonews.net）

## 三、书签信源覆盖明细

完整 560 域名逐条判定结果（含探测到的 RSS 地址和 RSSHub 路由名）见：
- `output_domains.csv`（Excel 可开，按书签数量排序）

要点：
- **24 个域名双通道可用**（原生 + RSSHub），建议优先用原生，稳定且快。
- **138 个域名只有原生 RSS**：绝大多数是 WordPress 系媒体 / 智库，直接订即可。
- **71 个域名只能靠 RSSHub**：Bloomberg、FT、WSJ、NYT、日经、早报、BBC、路透以及全部中文门户（新浪、观察者、环球、参考消息、华尔街见闻）和 Substack 系专栏。
- **327 个域名无覆盖**，但拆解后真实损失很小：130 条是 Google 搜索页；其余多为咨询报告页（PwC、McKinsey 报告库、Roland Berger）、期刊论文页（Lancet、Clarivate）、机构官网内页、微信公众号文章（mp.weixin.qq.com，可用 RSSHub 的微信公众号方案但需额外服务）。真正"新闻更新"类且两不沾的只有极少数（如 JPMorgan 研报页、Rand 报告页——这些适合用"网页监控"而非 RSS 补）。

## 四、技术方案：每分钟抓取 → 筛选 → 中文简报

推荐架构（全部开源免费、可本机运行）：

```
RSSHub 自部署 (Docker)          原生 RSS (162 源)
        |                            |
        +------------+---------------+
                     v
        feedparser 拉取（每分钟，增量去重）
                     v
        关键词/正则筛选（政治·经济·军事词表，可配）
                     v
        LLM 翻译 + 摘要（中文标题 + 一段话总结）
                     v
        python-docx 生成简报（与样例格式一致）
```

1. **采集层**：`feedparser` + 源清单 YAML；每源记录 last-guid，增量处理；并发 20+，560 源一轮 < 1 分钟可行。
2. **筛选层**：两级——① 源分类白名单（只跑政治/经济/军事类源）；② 标题关键词打分（war/sanction/rate/treasury/军演/制裁… 中英双语词表）。
3. **生成层**：LLM 产出「【信源】中文标题（作者）＋信源链接＋中文总结段落」，与样例 docx 完全一致；python-docx 落盘。
4. **调度**：本环境可用 Kimi Work 定时任务（widget task）每分钟跑采集，或本地 launchd + Python 脚本。
5. **注意**：Bloomberg/FT/WSJ 有付费墙，RSSHub 只给标题摘要——足够做简报标题筛选，正文总结需靠公开段落；每分钟频率对单源偏高，建议重要源 1 分钟、一般源 5-15 分钟分级。

## 五、文件清单

| 文件 | 内容 |
|---|---|
| `output_domains.csv` | 560 域名 × 书签数 × 原生RSS地址 × RSSHub路由 × 覆盖类别 |
| `input/final_matrix.json` | 同上，JSON 版 |
| `input/rsshub_ns.json` | RSSHub 1967 路由与域名映射（本次抓取） |
| `check_rss.py` | 原生 RSS 探测脚本，可复跑 |
