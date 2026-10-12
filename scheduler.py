#!/usr/bin/env python3
"""常驻调度器：按源分级间隔轮询，HTTP 条件请求（ETag/Last-Modified）降负载，
有新条目时立即跑筛选器。Ctrl+C 退出。

分级：
  fast   60s  —— 通讯社/快讯类高频源
  normal 300s —— 普通媒体（默认）
  slow   900s —— 智库/期刊类低频源

状态保存在 state/poll_state.json（每个源的 etag / modified / 下次到期时间）。
用法: python scheduler.py
"""
import json, subprocess, sys, time
import concurrent.futures as cf
from pathlib import Path

import feedparser
import yaml

from fetch import UA, entry_ts, MAX_AGE_HOURS

ROOT = Path(__file__).parent
STATE = ROOT / 'state'; STATE.mkdir(exist_ok=True)
POLL_STATE = STATE / 'poll_state.json'
SEEN = STATE / 'seen.json'
OUT = ROOT / 'output'; OUT.mkdir(exist_ok=True)

# ---- 分级名单（可按需调整）----
FAST_DOMAINS = {  # 60s：通讯社、财经快讯
    'reuters.com', 'bloomberg.com', 'apnews.com', 'ft.com', 'cnbc.com',
    'caixin.com', 'cls.cn', 'yicai.com', 'wallstreetcn.com', 'sina.com.cn',
}
SLOW_DOMAINS = {  # 900s：智库、期刊、研究类
    'atlanticcouncil.org', 'lowyinstitute.org', 'brookings.edu', 'cfr.org',
    'csis.org', 'rand.org', 'chathamhouse.org', 'carnegieendowment.org',
    'foreignaffairs.com', 'foreignpolicy.com', 'nature.com', 'science.org',
    'bcg.com', 'mckinsey.com', 'spglobal.com', 'hoover.org', 'aei.org',
    'piie.com', 'bruegel.org', 'moderndiplomacy.eu',
}
INTERVALS = {'fast': 60, 'normal': 300, 'slow': 900}

def tier_of(domain):
    if domain in FAST_DOMAINS:
        return 'fast'
    if domain in SLOW_DOMAINS:
        return 'slow'
    return 'normal'

def load_json(p, default):
    return json.loads(p.read_text()) if p.exists() else default

def fetch_conditional(src, st, timeout=12):
    """带 ETag/Last-Modified 的单源抓取。返回 (entries, err, new_state_fields)"""
    url = src.get('feed')
    if not url:
        return [], 'no-feed-url', {}
    kw = {'request_headers': {'User-Agent': UA}, 'resolve_relative_uris': True}
    if st.get('etag'):
        kw['etag'] = st['etag']
    if st.get('modified'):
        kw['modified'] = st['modified']
    try:
        d = feedparser.parse(url, **kw)
        if getattr(d, 'status', None) == 304:
            return [], None, {'unchanged': True}   # 内容未变，零解析成本
        if d.bozo and not d.entries:
            return [], f'parse-error: {str(d.bozo_exception)[:80]}', {}
        entries, now = [], time.time()
        for e in d.entries[:50]:
            ts = entry_ts(e)
            if ts is not None and now - ts > MAX_AGE_HOURS * 3600:
                continue
            entries.append({
                'source': src['domain'], 'via': src.get('via'),
                'title': e.get('title', '').strip(), 'link': e.get('link', ''),
                'published': e.get('published', e.get('updated', '')),
                'ts': ts, 'summary': (e.get('summary', '') or '')[:500],
            })
        new_st = {}
        if d.get('etag'):
            new_st['etag'] = d['etag']
        if d.get('modified'):
            new_st['modified'] = d['modified']
        return entries, (None if entries else 'empty-feed'), new_st
    except Exception as ex:
        return [], f'{type(ex).__name__}: {str(ex)[:80]}', {}

def run_round(sources, poll, force_all=False):
    now = time.time()
    due = [s for s in sources
           if force_all or now >= poll.get(s['domain'], {}).get('next_due', 0)]
    if not due:
        return 0, 0
    all_entries, failures = [], []
    with cf.ThreadPoolExecutor(20) as ex:
        futs = {ex.submit(fetch_conditional, s, poll.get(s['domain'], {})): s for s in due}
        for fut in cf.as_completed(futs):
            src = futs[fut]
            try:
                entries, err, new_st = fut.result()
            except Exception as ex2:
                entries, err, new_st = [], f'scheduler: {ex2}', {}
            st = poll.setdefault(src['domain'], {})
            st.update(new_st)
            st['last'] = int(now)
            # 失败时退避：下次按 3 倍间隔再来；成功按正常间隔
            interval = INTERVALS[tier_of(src['domain'])]
            st['next_due'] = int(now + interval * (3 if err and err != 'empty-feed' else 1))
            if err:
                failures.append({'domain': src['domain'], 'feed': src.get('feed', ''), 'error': err})
            all_entries.extend(entries)

    # 增量去重
    seen = load_json(SEEN, {})
    new_entries = []
    for e in all_entries:
        key = e.get('link') or (e['source'] + '|' + e['title'])
        if key not in seen:
            seen[key] = now
            new_entries.append(e)
    seen = {k: v for k, v in seen.items() if now - v < 7 * 86400}
    SEEN.write_text(json.dumps(seen))
    POLL_STATE.write_text(json.dumps(poll))

    if new_entries:
        ts = time.strftime('%Y%m%d_%H%M%S')
        ep = OUT / f'entries_{ts}.jsonl'
        with open(ep, 'w', encoding='utf-8') as f:
            for e in new_entries:
                f.write(json.dumps(e, ensure_ascii=False) + '\n')
        report = {'ran_at': ts, 'mode': 'scheduled', 'sources_due': len(due),
                  'sources_ok': len(due) - len(failures), 'sources_failed': len(failures),
                  'entries_fetched': len(all_entries), 'entries_new': len(new_entries),
                  'failures': failures}
        (OUT / f'fetch_report_{ts}.json').write_text(json.dumps(report, ensure_ascii=False, indent=1))
        # 立即跑筛选，与抓取批次配对
        subprocess.run([sys.executable, str(ROOT / 'filter.py'), str(ep)], cwd=ROOT,
                       capture_output=True)
    elif failures:
        # 没新内容也留一份报告，刷新信源健康状态
        ts = time.strftime('%Y%m%d_%H%M%S')
        (OUT / f'fetch_report_{ts}.json').write_text(json.dumps(
            {'ran_at': ts, 'mode': 'scheduled', 'sources_due': len(due),
             'sources_ok': len(due) - len(failures), 'sources_failed': len(failures),
             'entries_fetched': len(all_entries), 'entries_new': 0,
             'failures': failures}, ensure_ascii=False, indent=1))
    return len(due), len(new_entries)

def main():
    cfg = yaml.safe_load(open(ROOT / 'sources.yaml', encoding='utf-8'))
    disabled = set(load_json(STATE / 'disabled_sources.json', []))
    sources = [s for s in cfg['sources'] if s['domain'] not in disabled]
    poll = load_json(POLL_STATE, {})
    print(f'调度器启动：{len(sources)} 源，间隔 fast={INTERVALS["fast"]}s normal={INTERVALS["normal"]}s slow={INTERVALS["slow"]}s')
    first = True
    while True:
        t0 = time.time()
        due, new = run_round(sources, poll, force_all=first)
        first = False
        print(f'[{time.strftime("%H:%M:%S")}] 轮询 {due} 源，新增 {new} 条，耗时 {time.time()-t0:.1f}s', flush=True)
        time.sleep(15)  # 主循环节拍；源是否到期由 next_due 决定

if __name__ == '__main__':
    main()
