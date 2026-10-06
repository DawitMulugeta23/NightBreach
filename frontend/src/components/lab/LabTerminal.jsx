import { FitAddon } from '@xterm/addon-fit'
import { Terminal } from '@xterm/xterm'
import '@xterm/xterm/css/xterm.css'
import { useEffect, useRef, useState } from 'react'

import { createTerminalSession, terminalSocketUrl } from '../../api/labs.js'

export default function LabTerminal({ environmentId, machineName, active }) {
  const hostRef = useRef(null)
  const [status, setStatus] = useState('connecting')
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    if (!active || !hostRef.current) return undefined

    let disposed = false
    let socket = null

    const term = new Terminal({
      cursorBlink: true,
      fontFamily: 'ui-monospace, Menlo, Consolas, monospace',
      fontSize: 14,
      theme: { background: '#030914', foreground: '#d1fae5' },
    })
    const fit = new FitAddon()
    term.loadAddon(fit)
    term.open(hostRef.current)
    fit.fit()

    const send = (message) => {
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify(message))
      }
    }

    const inputSub = term.onData((data) => send({ type: 'input', data }))
    const resizeSub = term.onResize(({ cols, rows }) =>
      send({ type: 'resize', cols, rows }),
    )
    const observer = new ResizeObserver(() => {
      try {
        fit.fit()
      } catch {
        // The host element can be detached mid-resize.
      }
    })
    observer.observe(hostRef.current)

    async function connect() {
      try {
        const session = await createTerminalSession(environmentId, machineName)
        if (disposed) return

        socket = new WebSocket(terminalSocketUrl(session.session_id))

        socket.onopen = () => {
          setStatus('connected')
          send({ type: 'resize', cols: term.cols, rows: term.rows })
          term.focus()
        }

        socket.onmessage = (event) => {
          let message
          try {
            message = JSON.parse(event.data)
          } catch {
            return
          }

          if (message.type === 'output') term.write(message.data)
          else if (message.type === 'error') term.writeln(`\r\n[${message.message}]`)
          else if (message.type === 'exit') term.writeln('\r\n[session ended]')
        }

        socket.onclose = () => {
          if (!disposed) setStatus('closed')
        }
        socket.onerror = () => {
          if (!disposed) setStatus('error')
        }
      } catch (error) {
        if (!disposed) {
          setStatus('error')
          term.writeln(`\r\n[${error.message}]`)
        }
      }
    }

    connect()

    return () => {
      disposed = true
      observer.disconnect()
      inputSub.dispose()
      resizeSub.dispose()
      if (socket) socket.close()
      term.dispose()
    }
  }, [environmentId, machineName, active, attempt])

  const reconnect = () => {
    setStatus('connecting')
    setAttempt((value) => value + 1)
  }

  return (
    <div className="overflow-hidden rounded-xl border border-slate-800 bg-[#030914]">
      <div className="flex items-center justify-between border-b border-slate-800 px-4 py-2 text-xs">
        <span className="font-semibold uppercase tracking-wider text-slate-500">
          Attack machine terminal
        </span>
        <span className="flex items-center gap-3">
          <span
            className={
              status === 'connected'
                ? 'text-emerald-400'
                : status === 'connecting'
                  ? 'text-slate-400'
                  : 'text-orange-400'
            }
          >
            {status}
          </span>
          {(status === 'closed' || status === 'error') && (
            <button
              type="button"
              onClick={reconnect}
              className="rounded border border-slate-700 px-2 py-0.5 text-slate-300 hover:border-slate-500"
            >
              Reconnect
            </button>
          )}
        </span>
      </div>
      <div ref={hostRef} className="h-[380px] p-2" />
    </div>
  )
}
