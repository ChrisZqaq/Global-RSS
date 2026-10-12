#!/usr/bin/env python3
"""筛选层：从抓取条目里筛出 中国相关 / 全球科技前沿 / 经济金融，排除政治军事。
规则全部来自 filter_rules.yaml —— LLM 复盘学习只改 YAML，不改本文件。
用法: python filter.py [entries_xxx.jsonl]   默认用最新一批。"""
import json, re, sys, glob
from pathlib import Path

import yaml

RULES_PATH = Path(__file__).parent / 'filter_rules.yaml'

def load_rules():
    r = yaml.safe_load(open(RULES_PATH, encoding='utf-8'))
    return {
        'exclude': [w.lower() for w in r.get('exclude', [])],
        'keep': [w.lower() for w in r.get('keep_even_if_excluded', [])],
        'topics': {k: [w.lower() for w in v] for k, v in r.get('topics', {}).items()},
        'flash_re': [re.compile(p, re.I) for p in r.get('flash_patterns', [])],
        'flash_sources': set(r.get('flash_sources', [])),
        'th': r.get('thresholds', {}),
    }

RULES = load_rules()
MOVE_RE = re.compile(r'涨|跌|上扬|回落|走高|走低|%|％')

def classify(text):
    t = f' {text.lower()} '
    topics = [k for k, words in RULES['topics'].items()
              if any(w.strip() and f' {w} ' in t or w in t for w in words)]
    excluded = any(w in t for w in RULES['exclude'])
    kept = any(w in t for w in RULES['keep'])
    if excluded and not kept:
        return [], 'politics/military'
    return topics, None

def is_flash(e, src_route=''):
    th = RULES['th']
    title, summary = e.get('title', ''), e.get('summary', '')
    text_len = len(title) + len(summary)
    # 标题+摘要总长度过短：没有实质内容，直接丢弃
    if text_len < th.get('hard_min_text_len', 120):
        return 'too-short'
    # 纯开盘/收盘报数类标题：无论正文多长都是快讯，无条件丢弃
    if re.search(r'今日开盘|今日收盘|午评|收评|开盘报|收盘报|盘中异动', title):
        return 'flash-open-close'
    if text_len < th.get('min_text_len', 150) and any(r.search(title) for r in RULES['flash_re']):
        return 'flash-short'
    if any(r.search(title) for r in RULES['flash_re']) and text_len < th.get('flash_news_max_len', 300):
        return 'flash-news'
    # 标题堆叠多个行情动作词（市场综述式快讯），且正文不长
    if len(MOVE_RE.findall(title)) >= 3 and text_len < th.get('flash_wrap_max_len', 500):
        return 'flash-wrap'
    if any(k in (src_route or '') for k in RULES['flash_sources']) and text_len < th.get('flash_source_max_len', 250):
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
