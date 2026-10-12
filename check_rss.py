import json, re, ssl, socket, concurrent.futures as cf
import urllib.request, urllib.error

ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'}
FEED_PATHS = ['/feed','/feed/','/rss','/rss.xml','/feed.xml','/atom.xml','/index.xml','?feed=rss2']

def fetch(url, timeout=8):
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        data = r.read(300000)
        ct = r.headers.get('Content-Type','')
        return r.status, ct, data
    except Exception as e:
        return None, str(e)[:80], b''

def looks_like_feed(ct, data):
    head = data[:2000].lstrip()
    return (b'<rss' in head or b'<feed' in head or b'<rdf:RDF' in head
            or 'rss' in ct or 'atom' in ct or 'xml' in ct and (b'<rss' in data[:5000] or b'<feed' in data[:5000]))

def check(dom):
    scheme = 'https'
    st, ct, data = fetch(f'{scheme}://{dom}/')
    feeds = []
    if st and data:
        # link rel=alternate
        for m in re.finditer(rb'<link[^>]+>', data[:200000]):
            tag = m.group(0)
            if b'alternate' in tag and (b'application/rss' in tag or b'application/atom' in tag):
                hm = re.search(rb'href=["\']([^"\']+)', tag)
                if hm:
                    href = hm.group(1).decode('utf-8','ignore')
                    if href.startswith('/'): href = f'https://{dom}{href}'
                    feeds.append(href)
        if not feeds:
            for p in FEED_PATHS:
                st2, ct2, d2 = fetch(f'https://{dom}{p}')
                if st2==200 and looks_like_feed(ct2, d2):
                    feeds.append(f'https://{dom}{p}'); break
    return dom, feeds, (st if st else ct)

domains = json.load(open('input/domains_rsshub.json'))
out={}
with cf.ThreadPoolExecutor(40) as ex:
    futs = {ex.submit(check, d): d for d in domains}
    done=0
    for fut in cf.as_completed(futs):
        dom, feeds, info = fut.result()
        out[dom]={'feeds':feeds,'status':str(info)}
        done+=1
        if done%50==0: print(done, flush=True)
json.dump(out, open('input/rss_native.json','w'), ensure_ascii=False, indent=1)
have=[d for d,v in out.items() if v['feeds']]
print("native RSS:", len(have), "/", len(out))
