#!/usr/bin/env python3
"""Finance-RSS 管理界面后端 API。
启动: uvicorn server:app --port 8600 --reload
接口:
  GET  /api/stats            总览统计
  GET  /api/sources          信源列表（含可达状态）
  POST /api/sources          新增信源 {domain, feed?, via?}
  POST /api/sources/toggle   启停信源 {domain, enabled}
  GET  /api/entries          条目列表（含筛选状态、人工标记）
  POST /api/override         人工反转 {key, action: include|exclude|clear}
"""
import glob, json, time
from pathlib import Path

import yaml
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

ROOT = Path(__file__).parent
STATE = ROOT / 'state'; STATE.mkdir(exist_ok=True)
OVERRIDES = STATE / 'overrides.json'

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

def load_overrides():
    return json.loads(OVERRIDES.read_text()) if OVERRIDES.exists() else {}

def save_overrides(o):
    OVERRIDES.write_text(json.dumps(o, ensure_ascii=False, indent=1))

_names = None
def zh_name(domain):
    global _names
    if _names is None:
        p = ROOT / 'source_names.yaml'
        _names = yaml.safe_load(open(p, encoding='utf-8')) if p.exists() else {}
    return _names.get(domain, '')

def entry_ts(e):
    """条目的 epoch 时间：优先 ts 字段，否则解析 published"""
    if e.get('ts'):
        return e['ts']
    import email.utils
    try:
        return email.utils.parsedate_to_datetime(e.get('published', '')).timestamp()
    except Exception:
        return None

def entry_key(e):
    return e.get('link') or (e['source'] + '|' + e['title'])

def latest_entries():
    """抓取批次与筛选结果按时间戳配对，合并出带状态的条目列表"""
    ffiles = sorted(glob.glob(str(ROOT / 'output' / 'filtered_*.jsonl')))
    picked = {}
    ts = None
    if ffiles:
        ts = ffiles[-1].split('filtered_')[-1].replace('.jsonl', '')
        for line in open(ffiles[-1], encoding='utf-8'):
            if line.strip():
                e = json.loads(line)
                picked[entry_key(e)] = e.get('topics', [])
    entries = {}
    efiles = sorted(glob.glob(str(ROOT / 'output' / 'entries_*.jsonl')))
    # 优先与筛选结果同批次的抓取文件；再补充最近一批
    chosen = [f for f in efiles if ts and f'entries_{ts}' in f] or []
    chosen += efiles[-1:]
    for f in dict.fromkeys(chosen):
        for line in open(f, encoding='utf-8'):
            if line.strip():
                e = json.loads(line)
                entries[entry_key(e)] = e
    overrides = load_overrides()
    out = []
    now = time.time()
    for k, e in entries.items():
        ets = entry_ts(e)
        if ets is not None and now - ets > 12 * 3600:
            continue  # 界面只展示 12 小时内
        auto = k in picked
        ov = overrides.get(k)  # 'include' | 'exclude'
        final = (ov == 'include') if ov else (False if ov == 'exclude' else auto)
        out.append({
            'key': k, 'source': e['source'], 'source_zh': zh_name(e['source']),
            'title': e['title'], 'link': e.get('link', ''),
            'published': e.get('published', ''), 'ts': ets, 'summary': e.get('summary', '')[:300],
            'auto_selected': auto, 'topics': picked.get(k, []),
            'override': ov, 'final_selected': final,
        })
    out.sort(key=lambda x: -(x['ts'] or 0))
    return out

@app.get('/api/stats')
def stats():
    entries = latest_entries()
    sel = [e for e in entries if e['final_selected']]
    ov = sum(1 for e in entries if e['override'])
    cfg = yaml.safe_load(open(ROOT / 'sources.yaml', encoding='utf-8'))
    reports = sorted(glob.glob(str(ROOT / 'output' / 'fetch_report_*.json')))
    last = json.load(open(reports[-1])) if reports else {}
    real_failed = sum(1 for f in last.get('failures', []) if not str(f.get('error', '')).startswith('empty-feed'))
    return {
        'sources_total': len(cfg['sources']),
        'sources_ok': len(cfg['sources']) - real_failed,
        'last_fetch': last.get('ran_at', ''),
        'entries_total': len(entries),
        'selected': len(sel),
        'overrides': ov,
        'by_topic': {
            'china': sum(1 for e in sel if 'china' in e['topics']),
            'tech': sum(1 for e in sel if 'tech' in e['topics']),
            'econ': sum(1 for e in sel if 'econ' in e['topics']),
        },
    }

@app.get('/api/sources')
def sources():
    cfg = yaml.safe_load(open(ROOT / 'sources.yaml', encoding='utf-8'))
    disabled = set()
    if (STATE / 'disabled_sources.json').exists():
        disabled = set(json.loads((STATE / 'disabled_sources.json').read_text()))
    reports = sorted(glob.glob(str(ROOT / 'output' / 'fetch_report_*.json')))
    failed, quiet = set(), set()
    if reports:
        for f in json.load(open(reports[-1])).get('failures', []):
            if str(f.get('error', '')).startswith('empty-feed'):
                quiet.add(f['domain'])   # 可达但 12h 内无更新，不算失败
            else:
                failed.add(f['domain'])
    return [{
        'domain': s['domain'], 'name_zh': zh_name(s['domain']), 'via': s['via'],
        'site_url': f"https://{s['domain']}",
        'feed': s.get('feed', ''),
        'route': s.get('route', ''),
        'bookmarks': s.get('bookmarks', 0),
        'enabled': s['domain'] not in disabled,
        'healthy': s['domain'] not in failed,
        'quiet': s['domain'] in quiet,
    } for s in cfg['sources']]

class NewSource(BaseModel):
    domain: str
    feed: str = ''
    via: str = 'native'

@app.post('/api/sources')
def add_source(s: NewSource):
    cfg = yaml.safe_load(open(ROOT / 'sources.yaml', encoding='utf-8'))
    if any(x['domain'] == s.domain for x in cfg['sources']):
        return {'ok': False, 'msg': '已存在'}
    feed = s.feed or f'https://{s.domain}/feed'
    cfg['sources'].append({'domain': s.domain, 'bookmarks': 0, 'feed': feed, 'via': s.via})
    yaml.safe_dump(cfg, open(ROOT / 'sources.yaml', 'w', encoding='utf-8'),
                   allow_unicode=True, sort_keys=False)
    return {'ok': True}

class Toggle(BaseModel):
    domain: str
    enabled: bool

@app.post('/api/sources/toggle')
def toggle_source(t: Toggle):
    p = STATE / 'disabled_sources.json'
    disabled = set(json.loads(p.read_text())) if p.exists() else set()
    disabled.discard(t.domain) if t.enabled else disabled.add(t.domain)
    p.write_text(json.dumps(list(disabled)))
    return {'ok': True}

@app.get('/api/entries')
def entries():
    return latest_entries()

class Override(BaseModel):
    key: str
    action: str  # include | exclude | clear

@app.post('/api/override')
def set_override(o: Override):
    ov = load_overrides()
    if o.action == 'clear':
        ov.pop(o.key, None)
    else:
        ov[o.key] = o.action
    save_overrides(ov)
    return {'ok': True}
