import { useEffect, useMemo, useState } from 'react'
import { Check, X, Undo2, ExternalLink, ChevronDown, ChevronRight } from 'lucide-react'

export interface Entry {
  key: string
  source: string
  source_zh: string
  title: string
  link: string
  published: string
  ts: number | null
  summary: string
  auto_selected: boolean
  topics: string[]
  override: 'include' | 'exclude' | null
  override_reason: string
  final_selected: boolean
}

const QUICK_REASONS = ['主题不符', '太短/快讯', '信源不喜', '重要漏选']

const TOPIC_LABEL: Record<string, { text: string; cls: string }> = {
  china: { text: '中国', cls: 'bg-blue-50 text-blue-600 border-blue-200' },
  tech: { text: '科技', cls: 'bg-violet-50 text-violet-600 border-violet-200' },
  econ: { text: '经济', cls: 'bg-amber-50 text-amber-600 border-amber-200' },
}

function fmtTime(p: string) {
  const t = Date.parse(p)
  if (isNaN(t)) return p.slice(0, 16)
  const d = new Date(t)
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function EntryRow({ e, onOverride }: { e: Entry; onOverride: (key: string, action: string, reason?: string) => void }) {
  const selected = e.final_selected
  const [askReason, setAskReason] = useState<null | 'include' | 'exclude'>(null)
  const [reason, setReason] = useState('')
  const submit = (r: string) => {
    onOverride(e.key, askReason!, r)
    setAskReason(null); setReason('')
  }
  return (
    <div className={`group relative flex items-start gap-3 px-4 py-2.5 border-b border-slate-100 last:border-0 transition ${selected ? 'bg-white' : 'bg-transparent opacity-55 hover:opacity-80'}`}>
      <div className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${selected ? 'bg-emerald-500' : 'bg-slate-300'}`} />
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-1.5">
          <a href={e.link} target="_blank" rel="noreferrer"
            className={`text-[13.5px] leading-snug font-medium hover:text-indigo-600 hover:underline decoration-indigo-300 ${selected ? 'text-slate-800' : 'text-slate-500'}`}>
            {e.title}
          </a>
          <ExternalLink size={11} className="shrink-0 text-slate-300" />
        </div>
        <div className="mt-1 flex flex-wrap items-center gap-1.5 text-[11px]">
          <span className="text-slate-400">{fmtTime(e.published)}</span>
          {e.topics.map(t => (
            <span key={t} className={`rounded border px-1.5 py-px font-medium ${TOPIC_LABEL[t]?.cls ?? ''}`}>{TOPIC_LABEL[t]?.text ?? t}</span>
          ))}
          {e.override === 'include' && <span className="rounded border border-emerald-200 bg-emerald-50 px-1.5 py-px font-medium text-emerald-600">人工入选</span>}
          {e.override === 'exclude' && <span className="rounded border border-red-200 bg-red-50 px-1.5 py-px font-medium text-red-500">人工排除</span>}
          {e.override_reason && <span className="rounded border border-orange-200 bg-orange-50 px-1.5 py-px text-orange-500" title="人工理由">{e.override_reason}</span>}
        </div>
      </div>
      <div className="flex shrink-0 gap-1 opacity-0 transition group-hover:opacity-100">
        {selected ? (
          <button title="改为排除" onClick={() => setAskReason('exclude')}
            className="flex h-6 items-center gap-1 rounded border border-red-200 bg-white px-2 text-[11px] text-red-500 hover:bg-red-50">
            <X size={11} /> 排除
          </button>
        ) : (
          <button title="改为入选" onClick={() => setAskReason('include')}
            className="flex h-6 items-center gap-1 rounded border border-emerald-200 bg-white px-2 text-[11px] text-emerald-600 hover:bg-emerald-50">
            <Check size={11} /> 入选
          </button>
        )}
        {e.override && (
          <button title="清除人工标记" onClick={() => onOverride(e.key, 'clear')}
            className="flex h-6 items-center gap-1 rounded border border-slate-200 bg-white px-2 text-[11px] text-slate-400 hover:bg-slate-50">
            <Undo2 size={11} />
          </button>
        )}
      </div>
      {askReason && (
        <div className="absolute right-2 top-9 z-20 w-80 rounded-xl border border-slate-200 bg-white p-3 shadow-xl">
          <div className="mb-2 text-[12px] font-medium text-slate-600">
            {askReason === 'include' ? '人工入选' : '人工排除'} — 理由（可不填）
          </div>
          <div className="mb-2 flex flex-wrap gap-1">
            {QUICK_REASONS.map(r => (
              <button key={r} onClick={() => submit(r)}
                className="rounded-full border border-indigo-200 bg-indigo-50 px-2.5 py-1 text-[11px] text-indigo-600 hover:bg-indigo-100">
                {r}
              </button>
            ))}
          </div>
          <div className="flex gap-1.5">
            <input autoFocus value={reason} onChange={ev => setReason(ev.target.value)}
              onKeyDown={ev => ev.key === 'Enter' && submit(reason)}
              placeholder="自定义理由，回车确认"
              className="h-7 flex-1 rounded-md border border-slate-200 px-2 text-[12px] outline-none focus:border-indigo-300" />
            <button onClick={() => submit(reason)}
              className="h-7 rounded-md bg-indigo-600 px-2.5 text-[12px] text-white hover:bg-indigo-700">确定</button>
            <button onClick={() => { setAskReason(null); setReason('') }}
              className="h-7 rounded-md border border-slate-200 px-2 text-[12px] text-slate-400 hover:bg-slate-50">取消</button>
          </div>
        </div>
      )}
    </div>
  )
}

export default function EntriesView() {
  const [entries, setEntries] = useState<Entry[]>([])
  const [loading, setLoading] = useState(true)
  const [q, setQ] = useState('')
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({})

  const load = () => fetch('/api/entries').then(r => r.json()).then(d => { setEntries(d); setLoading(false) })
  useEffect(() => { load() }, [])

  const onOverride = async (key: string, action: string, reason = '') => {
    const entry = entries.find(e => e.key === key)
    await fetch('/api/override', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ key, action, reason, title: entry?.title || '', source: entry?.source || '' }),
    })
    load()
  }

  const [tag, setTag] = useState<'all' | 'china' | 'tech' | 'econ' | 'manual'>('all')

  const groups = useMemo(() => {
    const filtered = entries.filter(e => {
      if (q && !e.title.toLowerCase().includes(q.toLowerCase()) && !e.source.includes(q.toLowerCase()) && !(e.source_zh || '').includes(q)) return false
      if (tag === 'manual') return !!e.override
      if (tag !== 'all') return e.topics.includes(tag)
      return true
    })
    const m = new Map<string, Entry[]>()
    for (const e of filtered) {
      if (!m.has(e.source)) m.set(e.source, [])
      m.get(e.source)!.push(e)
    }
    const ts = (e: Entry) => e.ts || Date.parse(e.published) || 0
    return [...m.entries()]
      .map(([source, list]) => ({
        source,
        zh: list[0]?.source_zh || '',
        sel: list.filter(e => e.final_selected).sort((a, b) => ts(b) - ts(a)),
        rest: list.filter(e => !e.final_selected).sort((a, b) => ts(b) - ts(a)),
        latest: Math.max(...list.map(ts)),
      }))
      .filter(g => g.sel.length + g.rest.length > 0)
      .sort((a, b) => b.latest - a.latest)  // 有更新的组排前面
  }, [entries, q, tag])

  if (loading) return <div className="py-20 text-center text-sm text-slate-400">加载中…</div>

  const TAGS = [
    ['all', '全部', ''], ['china', '中国', 'text-blue-600'], ['tech', '科技', 'text-violet-600'],
    ['econ', '经济', 'text-amber-600'], ['manual', '人工标记', 'text-orange-500'],
  ] as const

  return (
    <div>
      <div className="mb-4 flex flex-wrap items-center gap-3">
        <input value={q} onChange={e => setQ(e.target.value)} placeholder="搜索标题或信源…"
          className="h-9 w-72 rounded-lg border border-slate-200 bg-white px-3 text-[13px] outline-none focus:border-indigo-300 focus:ring-2 focus:ring-indigo-100" />
        <div className="flex gap-1 rounded-lg bg-slate-100 p-1">
          {TAGS.map(([k, label, cls]) => (
            <button key={k} onClick={() => setTag(k)}
              className={`rounded-md px-3 py-1 text-[12px] font-medium transition ${tag === k ? `bg-white shadow-sm ${cls || 'text-indigo-700'}` : 'text-slate-500 hover:text-slate-700'}`}>
              {label}
            </button>
          ))}
        </div>
        <span className="text-[12px] text-slate-400">绿点 = 入选简报，灰色 = 已筛除；悬停可人工反转</span>
      </div>
      <div className="space-y-3">
        {groups.map(g => {
          const isCollapsed = collapsed[g.source]
          return (
            <div key={g.source} className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
              <button onClick={() => setCollapsed(c => ({ ...c, [g.source]: !c[g.source] }))}
                className="flex w-full items-center gap-2 bg-slate-50/70 px-4 py-2.5 text-left hover:bg-slate-100/70">
                {isCollapsed ? <ChevronRight size={14} className="text-slate-400" /> : <ChevronDown size={14} className="text-slate-400" />}
                <span className="text-[13px] font-semibold text-slate-700">{g.zh || g.source}</span>
                {g.zh && <span className="text-[11px] text-slate-400">{g.source}</span>}
                <span className="ml-auto text-[11px] text-slate-400">
                  <b className="text-emerald-600">{g.sel.length}</b> 入选 / {g.rest.length} 筛除
                </span>
              </button>
              {!isCollapsed && (
                <div>
                  {g.sel.map(e => <EntryRow key={e.key} e={e} onOverride={onOverride} />)}
                  {g.rest.map(e => <EntryRow key={e.key} e={e} onOverride={onOverride} />)}
                </div>
              )}
            </div>
          )
        })}
        {groups.length === 0 && <div className="py-20 text-center text-sm text-slate-400">没有匹配的条目</div>}
      </div>
    </div>
  )
}
