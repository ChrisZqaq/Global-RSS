import { useEffect, useMemo, useState } from 'react'
import { Plus, Globe, Rss } from 'lucide-react'

interface Source {
  domain: string
  via: string
  feed: string
  bookmarks: number
  enabled: boolean
  healthy: boolean
}

export default function SourcesView() {
  const [sources, setSources] = useState<Source[]>([])
  const [loading, setLoading] = useState(true)
  const [q, setQ] = useState('')
  const [domain, setDomain] = useState('')
  const [feed, setFeed] = useState('')
  const [msg, setMsg] = useState('')

  const load = () => fetch('/api/sources').then(r => r.json()).then(d => { setSources(d); setLoading(false) })
  useEffect(() => { load() }, [])

  const toggle = async (s: Source) => {
    await fetch('/api/sources/toggle', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ domain: s.domain, enabled: !s.enabled }) })
    load()
  }

  const add = async () => {
    if (!domain.trim()) return
    const r = await fetch('/api/sources', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ domain: domain.trim(), feed: feed.trim() }) })
    const d = await r.json()
    setMsg(d.ok ? `已添加 ${domain}` : d.msg || '添加失败')
    if (d.ok) { setDomain(''); setFeed('') }
    load()
  }

  const list = useMemo(() =>
    sources.filter(s => !q || s.domain.includes(q.toLowerCase()))
      .sort((a, b) => Number(b.enabled) - Number(a.enabled) || Number(b.healthy) - Number(a.healthy) || b.bookmarks - a.bookmarks),
    [sources, q])

  if (loading) return <div className="py-20 text-center text-sm text-slate-400">加载中…</div>

  return (
    <div>
      <div className="mb-4 flex flex-wrap items-center gap-2">
        <input value={domain} onChange={e => setDomain(e.target.value)} placeholder="域名，如 reuters.com"
          className="h-9 w-56 rounded-lg border border-slate-200 bg-white px-3 text-[13px] outline-none focus:border-indigo-300 focus:ring-2 focus:ring-indigo-100" />
        <input value={feed} onChange={e => setFeed(e.target.value)} placeholder="RSS 地址（可留空，自动尝试 /feed）"
          className="h-9 w-80 rounded-lg border border-slate-200 bg-white px-3 text-[13px] outline-none focus:border-indigo-300 focus:ring-2 focus:ring-indigo-100" />
        <button onClick={add} className="flex h-9 items-center gap-1.5 rounded-lg bg-indigo-600 px-4 text-[13px] font-medium text-white hover:bg-indigo-700">
          <Plus size={14} /> 添加信源
        </button>
        {msg && <span className="text-[12px] text-slate-500">{msg}</span>}
        <input value={q} onChange={e => setQ(e.target.value)} placeholder="搜索域名…"
          className="ml-auto h-9 w-48 rounded-lg border border-slate-200 bg-white px-3 text-[13px] outline-none focus:border-indigo-300 focus:ring-2 focus:ring-indigo-100" />
      </div>
      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        <table className="w-full text-[13px]">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50/70 text-left text-[11.5px] text-slate-400">
              <th className="px-4 py-2.5 font-medium">状态</th>
              <th className="px-4 py-2.5 font-medium">域名</th>
              <th className="px-4 py-2.5 font-medium">接入方式</th>
              <th className="px-4 py-2.5 font-medium">Feed 地址</th>
              <th className="px-4 py-2.5 text-right font-medium">启用</th>
            </tr>
          </thead>
          <tbody>
            {list.map(s => (
              <tr key={s.domain} className={`border-b border-slate-100 last:border-0 ${s.enabled ? '' : 'opacity-45'}`}>
                <td className="px-4 py-2">
                  <span className={`inline-flex items-center gap-1.5 text-[11.5px] ${s.healthy ? 'text-emerald-600' : 'text-red-500'}`}>
                    <span className={`h-2 w-2 rounded-full ${s.healthy ? 'bg-emerald-500' : 'bg-red-400'}`} />
                    {s.healthy ? '正常' : '失败'}
                  </span>
                </td>
                <td className="px-4 py-2 font-medium text-slate-700">{s.domain}</td>
                <td className="px-4 py-2">
                  <span className={`inline-flex items-center gap-1 rounded border px-1.5 py-px text-[11px] font-medium ${s.via === 'native' ? 'border-sky-200 bg-sky-50 text-sky-600' : 'border-orange-200 bg-orange-50 text-orange-600'}`}>
                    {s.via === 'native' ? <Rss size={10} /> : <Globe size={10} />}
                    {s.via === 'native' ? '原生 RSS' : 'RSSHub'}
                  </span>
                </td>
                <td className="max-w-[320px] truncate px-4 py-2 text-[12px] text-slate-400">{s.feed}</td>
                <td className="px-4 py-2 text-right">
                  <button onClick={() => toggle(s)}
                    className={`relative inline-flex h-5 w-9 items-center rounded-full transition ${s.enabled ? 'bg-indigo-600' : 'bg-slate-300'}`}>
                    <span className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white transition ${s.enabled ? 'translate-x-5' : 'translate-x-1'}`} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-3 text-[12px] text-slate-400">共 {list.length} 个信源 · 红色状态为最近一轮抓取失败（多为需代理或付费墙）</div>
    </div>
  )
}
