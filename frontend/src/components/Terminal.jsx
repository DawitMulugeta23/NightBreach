import React, { useEffect, useRef, useState } from 'react'
import { Terminal as XTerm } from '@xterm/xterm'
import { FitAddon } from '@xterm/addon-fit'
import '@xterm/xterm/css/xterm.css'
import { tokenStorage } from '../utils/api'
import { usePreferences } from '../context/PreferencesContext'

function Terminal({ height = '100%', autoStart = false, onClose }) {
  const containerRef = useRef(null)
  const termRef = useRef(null)
  const fitRef = useRef(null)
  const wsRef = useRef(null)
  const [started, setStarted] = useState(false)
  const [connected, setConnected] = useState(false)
  const [error, setError] = useState('')
  const { prefs } = usePreferences()

  // React to preference changes on an already-open terminal
  useEffect(() => {
    const term = termRef.current
    if (!term) return
    term.options.fontSize = prefs.terminalFontSize
    term.options.fontFamily = prefs.terminalFontFamily
    term.options.cursorStyle = prefs.terminalCursorStyle
    term.options.cursorBlink = prefs.terminalCursorBlink
    term.options.scrollback = prefs.terminalScrollback
    try { fitRef.current?.fit() } catch {}
  }, [
    prefs.terminalFontSize,
    prefs.terminalFontFamily,
    prefs.terminalCursorStyle,
    prefs.terminalCursorBlink,
    prefs.terminalScrollback,
  ])

  useEffect(() => {
    if (autoStart) {
      const t = setTimeout(() => startTerminal(), 50)
      return () => clearTimeout(t)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autoStart])

  useEffect(() => {
    return () => {
      try { wsRef.current?.close() } catch {}
      try { termRef.current?.dispose() } catch {}
    }
  }, [])

  const startTerminal = () => {
    if (!containerRef.current || started) return
    setError('')

    const term = new XTerm({
      cursorBlink: prefs.terminalCursorBlink,
      cursorStyle: prefs.terminalCursorStyle,
      fontSize: prefs.terminalFontSize,
      fontFamily: prefs.terminalFontFamily,
      // Full 16-color palette — maps to the ANSI codes bash/ls emit.
      theme: {
        background: '#0a0a0a',
        foreground: '#e5e7eb',
        cursor: '#34d399',
        cursorAccent: '#0a0a0a',
        selectionBackground: '#34d39940',

        // Standard ANSI palette
        black:   '#1f2937',
        red:     '#ef4444',
        green:   '#34d399',
        yellow:  '#fbbf24',
        blue:    '#60a5fa',
        magenta: '#c084fc',
        cyan:    '#22d3ee',
        white:   '#e5e7eb',

        // Bright variants
        brightBlack:   '#6b7280',
        brightRed:     '#f87171',
        brightGreen:   '#6ee7b7',
        brightYellow:  '#fcd34d',
        brightBlue:    '#93c5fd',
        brightMagenta: '#d8b4fe',
        brightCyan:    '#67e8f9',
        brightWhite:   '#ffffff',
      },
      convertEol: true,
      allowProposedApi: true,
      scrollback: prefs.terminalScrollback,
    })
    const fit = new FitAddon()
    term.loadAddon(fit)
    term.open(containerRef.current)
    setTimeout(() => { try { fit.fit() } catch {} }, 30)
    termRef.current = term
    fitRef.current = fit

    const token = tokenStorage.get()
    if (!token) {
      setError('Not authenticated. Please log in.')
      return
    }

    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const backendHost = `${window.location.hostname}:8000`
    const ws = new WebSocket(`${protocol}://${backendHost}/ws/terminal?token=${encodeURIComponent(token)}`)
    wsRef.current = ws
    ws.binaryType = 'arraybuffer'

    ws.onopen = () => {
      setConnected(true)
      term.writeln('\x1b[32m● Connected to NightBreach\x1b[0m')
      term.writeln('')
      try { fit.fit() } catch {}
    }

    ws.onmessage = (event) => {
      const data = event.data
      if (typeof data === 'string') {
        term.write(data)
      } else {
        const text = new TextDecoder().decode(new Uint8Array(data))
        term.write(text)
      }
    }

    ws.onclose = (event) => {
      setConnected(false)
      if (event.code === 4401) {
        term.writeln('\r\n\x1b[31m● Session expired. Please log in again.\x1b[0m')
      } else {
        term.writeln('\r\n\x1b[33m● Disconnected.\x1b[0m')
      }
    }

    ws.onerror = () => {
      setError('WebSocket connection error. Is the backend running?')
    }

    term.onData((data) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(data)
      }
    })

    const ro = new ResizeObserver(() => {
      try { fit.fit() } catch {}
    })
    ro.observe(containerRef.current)

    setStarted(true)
  }

  const handleClose = () => {
    try { wsRef.current?.close() } catch {}
    try { termRef.current?.dispose() } catch {}
    wsRef.current = null
    termRef.current = null
    setStarted(false)
    setConnected(false)
    if (onClose) onClose()
  }

  return (
    <div className="rounded-2xl bg-white dark:bg-neutral-950 border border-neutral-200 dark:border-neutral-800 overflow-hidden flex flex-col h-full">
      <div className="flex items-center justify-between px-4 py-2.5 bg-neutral-50 dark:bg-neutral-900 border-b border-neutral-200 dark:border-neutral-800 flex-shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-red-500"></div>
          <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
          <div className="w-3 h-3 rounded-full bg-green-500"></div>
          <span className="ml-3 text-xs text-neutral-600 dark:text-neutral-400 font-mono">terminal — nightbreach</span>
          {connected && (
            <span className="ml-2 text-[10px] text-emerald-400 flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              live
            </span>
          )}
        </div>
        <button
          onClick={handleClose}
          className="text-xs text-neutral-600 dark:text-neutral-400 hover:text-red-400 transition-colors flex items-center gap-1"
        >
          <i className="fas fa-times"></i>
          Close
        </button>
      </div>

      <div className="relative flex-1 min-h-0 bg-[#0a0a0a]">
        {!started && (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-4 z-10 bg-white dark:bg-neutral-950">
            <i className="fas fa-terminal text-5xl text-emerald-400"></i>
            <p className="text-neutral-600 dark:text-neutral-400 text-sm text-center px-4">
              Connecting to your sandbox...
            </p>
            <button
              onClick={startTerminal}
              className="btn-primary px-6 py-3 text-sm flex items-center gap-2"
            >
              <i className="fas fa-play"></i>
              Start CLI
            </button>
            {error && (
              <p className="text-xs text-red-400 px-4 text-center">
                <i className="fas fa-circle-exclamation mr-1"></i>
                {error}
              </p>
            )}
          </div>
        )}
        <div
          ref={containerRef}
          className="absolute inset-0"
          style={{ padding: 0, margin: 0 }}
        />
      </div>
    </div>
  )
}

export default Terminal
