#!/usr/bin/env python3
"""筛选层：从抓取条目里筛出 中国相关 / 全球科技前沿 / 经济金融，排除政治军事。
用法: python filter.py [entries_xxx.jsonl]   默认用最新一批。"""
import json, re, sys, glob

# ---- 排除词：政治 / 军事（命中且不含保留词时丢弃）----
EXCLUDE = [
    'war', 'missile', 'military', 'army', 'navy', 'troops', 'weapon', 'drone strike',
    'election', 'senate', 'congress', 'parliament', 'ballot', 'campaign rally',
    'coup', 'protest', 'indict', 'verdict', 'impeach', 'geopolitical tension',
    '战争', '导弹', '军演', '军队', '武器', '选举', '议会', '政变', '弹劾', '抗议',
]
# ---- 保留词：即使含排除词也保留（政军背景下的经济/科技新闻仍要）----
KEEP_EVEN_IF_EXCLUDED = [
    'sanction', 'tariff', 'trade', 'export control', 'chip ban', 'supply chain',
    '制裁', '关税', '出口管制', '贸易', '供应链', '汇率', '利率',
]
# ---- 主题词 ----
TOPICS = {
    'china': [
        'china', 'chinese', 'beijing', 'shanghai', 'shenzhen', 'hong kong', 'taiwan',
        'xi jinping', 'li qiang', 'pboc', 'yuan', 'renminbi', 'brics',
        '中国', '北京', '上海', '深圳', '香港', '台湾', '人民币', '央行', '国务院', '发改委',
    ],
    'tech': [
        ' ai ', 'artificial intelligence', 'llm', 'chatgpt', 'openai', 'anthropic',
        'deepseek', 'semiconductor', 'chip', 'nvidia', 'tsmc', 'quantum', 'robot',
        'biotech', 'spacex', 'satellite', 'battery', 'ev ', 'electric vehicle',
        'data center', 'supercomput', '6g', '5g', 'photon', 'fusion',
        '人工智能', '大模型', '芯片', '半导体', '量子', '机器人', '商业航天', '固态电池', '核聚变',
    ],
    'econ': [
        'fed', 'federal reserve', 'interest rate', 'rate cut', 'rate hike', 'inflation',
        'treasury', 'bond', 'yield', 'stock market', 'wall street', 'nasdaq', 's&p',
        'gdp', 'cpi', 'pmi', 'recession', 'central bank', 'ecb', 'boj', 'imf', 'world bank',
        'oil price', 'gold price', 'dollar', 'currency', 'ipo', 'earnings', 'tariff',
        'sanction', 'trade war', 'supply chain', 'debt', 'deficit', 'stimulus',
        '美联储', '降息', '加息', '通胀', '国债', '收益率', '股市', '经济', '金融',
        '央行', '财政', '油价', '金价', '美元', '贸易', '关税', '制裁', '债',
    ],
}

def classify(text):
    t = f' {text.lower()} '
    topics = [k for k, words in TOPICS.items()
              if any(w.strip() and f' {w} ' in t or w in t for w in words)]
    excluded = any(w in t for w in EXCLUDE)
    kept = any(w in t for w in KEEP_EVEN_IF_EXCLUDED)
    if excluded and not kept:
        return [], 'politics/military'
    return topics, None

# ---- 快讯/短讯模式：开盘收盘、盘中涨跌、一句话行情 ----
FLASH_PATTERNS = [
    r'高開|高开|低開|低开|收涨|收跌|漲停|涨停|跌停|午盘|早盘|收盘报|开盘报',
    r'今日开盘|今日收盘|午评|收评|盘前|盘中',
    r'快讯|快訊|实时新闻|滚动新闻',
    r'\b(markets?|stocks?|shares?|futures?)\s+(open|close)s?\s+(higher|lower|up|down|flat)\b',
    r'\b(open|close)s?\s+(up|down)\s+\d',
    r'^[A-Z][^.!?]{0,80}(rise|fell|rose|gain|drop)s?\s+\d+(\.\d+)?%',
    r'开盘.{0,20}[涨跌]\s*\d|收[盘盡].{0,20}[涨跌]\s*\d',
    r'^\S{2,10}[：:]\s*.{0,60}[涨跌]幅?\s*\d+(\.\d+)?%',
]
FLASH_RE = [re.compile(p, re.I) for p in FLASH_PATTERNS]
MOVE_RE = re.compile(r'涨|跌|上扬|回落|走高|走低|%|％')

# 快讯类源（滚动短讯源，整体降权：只有足够长的才保留）
FLASH_SOURCES = {'sina', 'rollnews', 'live', 'telegraph', 'kuaixun'}

MIN_TEXT_LEN = 150   # 标题+摘要低于此长度视为太短
MIN_TITLE_LEN = 12   # 标题本身太短的（如只有几个字的快讯标题）

def is_flash(e, src_route=''):
    title, summary = e.get('title', ''), e.get('summary', '')
    text_len = len(title) + len(summary)
    # 标题+摘要总长度过短：没有实质内容，直接丢弃
    if text_len < 120:
        return 'too-short'
    # 纯开盘/收盘报数类标题：无论正文多长都是快讯，无条件丢弃
    if re.search(r'今日开盘|今日收盘|午评|收评|开盘报|收盘报|盘中异动', title):
        return 'flash-open-close'
    if text_len < MIN_TEXT_LEN and any(r.search(title) for r in FLASH_RE):
        return 'flash-short'
    if any(r.search(title) for r in FLASH_RE) and text_len < 300:
        return 'flash-news'
    # 标题堆叠多个行情动作词（市场综述式快讯），且正文不长
    if len(MOVE_RE.findall(title)) >= 3 and text_len < 500:
        return 'flash-wrap'
    if any(k in (src_route or '') for k in FLASH_SOURCES) and text_len < 250:
        return 'flash-source'
    return None

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else sorted(glob.glob('output/entries_*.jsonl'))[-1]
    entries = [json.loads(l) for l in open(path, encoding='utf-8') if l.strip()]
    picked, dropped = [], []
    for e in entries:
        flash = is_flash(e)
        if flash:
            dropped.append((e, flash)); continue
        topics, reason = classify(e.get('title', '') + ' ' + e.get('summary', ''))
        if topics:
            e['topics'] = topics
            picked.append(e)
        else:
            dropped.append((e, reason or 'off-topic'))
    out = path.replace('entries_', 'filtered_')
    with open(out, 'w', encoding='utf-8') as f:
        for e in picked:
            f.write(json.dumps(e, ensure_ascii=False) + '\n')
    from collections import Counter
    print(f'输入 {len(entries)} 条 -> 入选 {len(picked)} 条 ({len(picked)/max(len(entries),1):.0%})')
    print('主题分布:', Counter(t for e in picked for t in e['topics']).most_common())
    print('丢弃原因:', Counter(r for _, r in dropped).most_common())
    print('\n入选样例:')
    for e in picked[:15]:
        print(f"  [{'/'.join(e['topics'])}] [{e['source']}] {e['title'][:65]}")

if __name__ == '__main__':
    main()
