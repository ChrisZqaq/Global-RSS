import { useEffect, useState } from 'react'
import { Newspaper, Database, CheckCircle2, PencilLine, RefreshCw } from 'lucide-react'
import EntriesView from './pages/Entries'
import SourcesView from './pages/Sources'

export interface Stats {
  sources_total: number
  sources_ok: number
  last_fetch: string
  entries_total: number
  selected: number
  overrides: number
  by_topic: { china: number; tech: number; econ: number }
}

export default function App() {
  const [tab, setTab] = useState<'entries' | 'sources'>('entries')
  const [stats, setStats] = useState<Stats | null>(null)
  const [err, setErr] = useState('')

  const loadStats = () => {
    fetch('/api/stats')
      .then(r => r.json())
      .then(setStats)
      .catch(() => setErr('后端未启动：请先运行 uvicorn server:app --port 8600'))
  }
  useEffect(loadStats, [])

  return (
    <div className="min-h-screen bg-[#f6f7f9] text-slate-800">
      <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center gap-6 px-6 py-3">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 text-white">
              <Newspaper size={17} />
            </div>
            <div>
              <div className="text-[15px] font-semibold leading-tight">全球资讯简报</div>
              <div className="text-[11px] text-slate-400 leading-tight">Finance-RSS 控制台</div>
            </div>
          </div>
          <nav className="flex gap-1 rounded-lg bg-slate-100 p-1">
            {([['entries', '条目浏览'], ['sources', '信源管理']] as const).map(([k, label]) => (
              <button key={k} onClick={() => setTab(k)}
                className={`rounded-md px-4 py-1.5 text-[13px] font-medium transition ${tab === k ? 'bg-white text-indigo-700 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}>
                {label}
              </button>
            ))}
          </nav>
          <button onClick={loadStats} className="ml-auto flex items-center gap-1.5 rounded-md border border-slate-200 px-3 py-1.5 text-[12px] text-slate-500 hover:bg-slate-50">
            <RefreshCw size={13} /> 刷新
          </button>
        </div>
        {stats && (
          <div className="mx-auto flex max-w-6xl flex-wrap gap-x-6 gap-y-1 px-6 pb-2.5 text-[12px] text-slate-500">
            <span className="flex items-center gap-1"><Database size={12} className="text-slate-400" />信源 <b className="text-slate-700">{stats.sources_ok}/{stats.sources_total}</b> 可达</span>
            <span>条目 <b className="text-slate-700">{stats.entries_total}</b></span>
            <span className="flex items-center gap-1"><CheckCircle2 size={12} className="text-emerald-500" />入选 <b className="text-emerald-600">{stats.selected}</b></span>
            <span>中国 <b className="text-blue-600">{stats.by_topic.china}</b> · 科技 <b className="text-violet-600">{stats.by_topic.tech}</b> · 经济 <b className="text-amber-600">{stats.by_topic.econ}</b></span>
            <span className="flex items-center gap-1"><PencilLine size={12} className="text-orange-400" />人工校正 <b className="text-orange-500">{stats.overrides}</b></span>
            <span className="text-slate-400">最近抓取 {stats.last_fetch}</span>
          </div>
        )}
      </header>
      {err && <div className="mx-auto mt-4 max-w-6xl rounded-lg border border-red-200 bg-red-50 px-4 py-2.5 text-[13px] text-red-600">{err}</div>}
      <main className="mx-auto max-w-6xl px-6 py-5">
        {tab === 'entries' ? <EntriesView /> : <SourcesView />}
      </main>
    </div>
  )
}
