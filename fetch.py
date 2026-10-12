#!/usr/bin/env python3
"""信源获取层：并发抓取 sources.yaml 中的 RSS，输出统一 JSONL + 状态报告。"""
import json, ssl, sys, time, calendar
import concurrent.futures as cf
from pathlib import Path

import feedparser
import yaml

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36")

MAX_AGE_HOURS = 12  # 只保留 12 小时内的新闻；时间无法解析的保留但打标

def entry_ts(e):
    """feedparser 解析出的结构化时间 -> epoch；无则 None。
    注意 published_parsed 是 UTC struct_time，必须用 timegm 而非 mktime。"""
    t = e.get('published_parsed') or e.get('updated_parsed')
    try:
        return calendar.timegm(t) if t else None
    except Exception:
        return None

def fetch_one(src, timeout=12):
    """抓一个源，返回 (source_meta, entries, error)"""
    url = src.get('feed')
    if not url:
        return src, [], 'no-feed-url'
    try:
        d = feedparser.parse(url, request_headers={'User-Agent': UA},
                             handlers=[], resolve_relative_uris=True)
        if d.bozo and not d.entries:
            return src, [], f'parse-error: {str(d.bozo_exception)[:80]}'
        entries = []
        now = time.time()
        for e in d.entries[:50]:
            ts = entry_ts(e)
            if ts is not None and now - ts > MAX_AGE_HOURS * 3600:
                continue  # 超过 12 小时的丢弃
            entries.append({
                'source': src['domain'],
                'via': src.get('via'),
                'title': e.get('title', '').strip(),
                'link': e.get('link', ''),
                'published': e.get('published', e.get('updated', '')),
                'ts': ts,  # None = 时间未知
                'summary': (e.get('summary', '') or '')[:500],
            })
        return src, entries, None if entries else 'empty-feed'
    except Exception as ex:
        return src, [], f'{type(ex).__name__}: {str(ex)[:80]}'

def main():
    cfg = yaml.safe_load(open('sources.yaml', encoding='utf-8'))
    sources = cfg['sources']
    only = sys.argv[1] if len(sys.argv) > 1 else None  # 'native' 只跑原生
    if only:
        sources = [s for s in sources if s['via'] == only]

    results, failures = [], []
    out_dir = Path('output'); out_dir.mkdir(exist_ok=True)
    t0 = time.time()
    with cf.ThreadPoolExecutor(30) as ex:
        futs = {ex.submit(fetch_one, s): s for s in sources}
        for i, fut in enumerate(cf.as_completed(futs), 1):
            src, entries, err = fut.result()
            if err:
                failures.append({'domain': src['domain'], 'feed': src.get('feed', ''),
                                 'error': err})
            else:
                results.extend(entries)
            if i % 40 == 0:
                print(f'  {i}/{len(sources)}', flush=True)

    # ---- 增量去重：用 state/seen.json 记住已见过的条目，只输出新增的 ----
    state_dir = Path('state'); state_dir.mkdir(exist_ok=True)
    seen_path = state_dir / 'seen.json'
    seen = json.loads(seen_path.read_text()) if seen_path.exists() else {}
    now = time.time()
    new_entries = []
    for e in results:
        key = e.get('link') or (e['source'] + '|' + e['title'])
        if key not in seen:
            seen[key] = now
            new_entries.append(e)
    # 状态裁剪：只保留最近 7 天，防止无限膨胀
    seen = {k: v for k, v in seen.items() if now - v < 7 * 86400}
    seen_path.write_text(json.dumps(seen))

    ts = time.strftime('%Y%m%d_%H%M%S')
    with open(out_dir / f'entries_{ts}.jsonl', 'w', encoding='utf-8') as f:
        for e in new_entries:
            f.write(json.dumps(e, ensure_ascii=False) + '\n')
    report = {
        'ran_at': ts, 'elapsed_sec': round(time.time() - t0, 1),
        'sources_total': len(sources),
        'sources_ok': len(sources) - len(failures),
        'sources_failed': len(failures),
        'entries_fetched': len(results),
        'entries_new': len(new_entries),
        'entries_dup': len(results) - len(new_entries),
        'failures': failures,
    }
    with open(out_dir / f'fetch_report_{ts}.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in report.items() if k != 'failures'},
                     ensure_ascii=False, indent=1))

if __name__ == '__main__':
    main()
