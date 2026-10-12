// 一键启动：FastAPI 后端 (8600) + Vite 前端 (7100)
// 后端日志写入 app/backend.log，便于排查
import { spawn } from 'child_process'
import fs from 'fs'
import os from 'os'
import path from 'path'
import { fileURLToPath } from 'url'

const appDir = path.dirname(path.dirname(fileURLToPath(import.meta.url)))
const root = path.dirname(appDir) // Finance-RSS 项目根目录
const logStream = fs.createWriteStream(path.join(appDir, 'backend.log'), { flags: 'a' })

// 按优先级找装有依赖的 Python：Kimi 托管运行时 > 系统 python3 > python
const candidates = [
  path.join(os.homedir(), 'Library/Application Support/kimi-desktop/daimon-share/daimon/runtime/python/.venv/bin/python3'),
  'python3',
  'python',
]

let idx = 0
function startBackend() {
  if (idx >= candidates.length) {
    logStream.write('[dev] no usable python found\n')
    return
  }
  const py = candidates[idx++]
  logStream.write(`[dev] trying python: ${py}\n`)
  const backend = spawn(py, ['-m', 'uvicorn', 'server:app', '--port', '8600'], { cwd: root })
  backend.stdout.pipe(logStream)
  backend.stderr.pipe(logStream)
  let exited = false
  backend.on('error', () => { exited = true; startBackend() })
  backend.on('exit', code => {
    if (!exited && code && code !== 0 && idx < candidates.length) {
      logStream.write(`[dev] ${py} exited ${code}, trying next\n`)
      startBackend()
    }
  })
  return backend
}

let backend = startBackend()
const frontend = spawn('npx', ['vite', '--port', '7100'], { cwd: appDir, stdio: 'inherit' })

const shutdown = () => { frontend.kill(); process.exit(0) }
process.on('SIGINT', shutdown)
process.on('SIGTERM', shutdown)
