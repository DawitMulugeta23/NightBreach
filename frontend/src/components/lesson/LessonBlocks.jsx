import {
  Check,
  Copy,
  Info,
  Lightbulb,
  ShieldAlert,
  Terminal,
  TriangleAlert,
} from 'lucide-react'
import { useState } from 'react'

async function copyText(text) {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text)
      return true
    }
  } catch {
    // fall through to the legacy path
  }

  // Plain-HTTP origins such as http://192.168.x.x have no navigator.clipboard.
  const area = document.createElement('textarea')
  area.value = text
  area.style.position = 'fixed'
  area.style.opacity = '0'
  document.body.appendChild(area)
  area.select()

  let ok = false
  try {
    ok = document.execCommand('copy')
  } catch {
    ok = false
  }

  document.body.removeChild(area)
  return ok
}

function LessonHeading({ content }) {
  const text = content.text || ''
  if (Number(content.level) >= 3) {
    return <h3 className="pt-2 text-lg font-semibold text-slate-900">{text}</h3>
  }
  return (
    <h2 className="border-b border-slate-200 pb-2 pt-4 text-2xl font-bold text-slate-900">
      {text}
    </h2>
  )
}

function LessonText({ content }) {
  return (
    <p className="whitespace-pre-line text-[15px] leading-7 text-slate-700">
      {content.text}
    </p>
  )
}

const SHELL_LANGUAGES = ['bash', 'sh', 'shell', 'zsh']

function CodeBlock({ content }) {
  const [copied, setCopied] = useState(false)
  const code = content.code ?? content.text ?? ''
  const language = String(content.language || 'text').toLowerCase()
  const isShell = SHELL_LANGUAGES.includes(language)
  const breakdown = Array.isArray(content.breakdown) ? content.breakdown : []

  async function handleCopy() {
    if (await copyText(code)) {
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    }
  }

  return (
    <div className="overflow-hidden rounded-xl border border-slate-800 bg-[#030914] shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-800 px-4 py-2">
        <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">
          {language}
        </span>
        <button
          type="button"
          onClick={handleCopy}
          className="inline-flex items-center gap-1.5 rounded-md px-2 py-1 text-[11px] font-semibold uppercase tracking-wider text-slate-400 transition hover:bg-slate-800/60 hover:text-white"
        >
          {copied ? (
            <Check className="h-3.5 w-3.5 text-emerald-400" />
          ) : (
            <Copy className="h-3.5 w-3.5" />
          )}
          {copied ? 'Copied' : 'Copy'}
        </button>
      </div>

      <pre className="nb-scrollbar overflow-x-auto p-4 font-mono text-sm leading-7 text-emerald-300">
        {code.split('\n').map((line, index) => {
          const isCommand =
            isShell && line.trim() !== '' && !line.trim().startsWith('#')
          return (
            <div key={index}>
              {isCommand && (
                <span className="select-none text-slate-600">$ </span>
              )}
              {line === '' ? '\u00a0' : line}
            </div>
          )
        })}
      </pre>

      {breakdown.length > 0 && (
        <div className="border-t border-slate-800 bg-slate-900/60 px-4 py-3">
          <div className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
            What each part does
          </div>
          <dl className="space-y-2.5">
            {breakdown.map((item, index) => (
              <div
                key={index}
                className="grid gap-1 sm:grid-cols-[minmax(0,190px)_minmax(0,1fr)] sm:gap-4"
              >
                <dt>
                  <code className="rounded bg-slate-800 px-1.5 py-0.5 font-mono text-[13px] text-cyan-300">
                    {item.part}
                  </code>
                </dt>
                <dd className="text-sm leading-6 text-slate-300">
                  {item.meaning}
                </dd>
              </div>
            ))}
          </dl>
        </div>
      )}
    </div>
  )
}

function TerminalOutput({ content }) {
  return (
    <div className="overflow-hidden rounded-xl border border-slate-800 bg-black shadow-sm">
      <div className="flex items-center gap-2 border-b border-slate-800 px-4 py-2">
        <Terminal className="h-3.5 w-3.5 text-slate-500" />
        <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">
          Terminal output
        </span>
      </div>
      <pre className="nb-scrollbar overflow-x-auto p-4 font-mono text-sm leading-7 text-slate-200">
        {content.text}
      </pre>
    </div>
  )
}

const CALLOUT_STYLES = {
  important: {
    icon: ShieldAlert,
    box: 'border-blue-200 bg-blue-50',
    accent: 'text-blue-700',
  },
  tip: {
    icon: Lightbulb,
    box: 'border-emerald-200 bg-emerald-50',
    accent: 'text-emerald-700',
  },
  warning: {
    icon: TriangleAlert,
    box: 'border-amber-200 bg-amber-50',
    accent: 'text-amber-700',
  },
  info: {
    icon: Info,
    box: 'border-slate-200 bg-slate-50',
    accent: 'text-slate-700',
  },
}

function Callout({ content }) {
  const style =
    CALLOUT_STYLES[String(content.type || '').toLowerCase()] ||
    CALLOUT_STYLES.info
  const Icon = style.icon

  return (
    <div className={`flex gap-4 rounded-xl border p-5 ${style.box}`}>
      <Icon className={`mt-0.5 h-5 w-5 shrink-0 ${style.accent}`} />
      <div>
        {content.title && (
          <div className={`text-sm font-bold ${style.accent}`}>
            {content.title}
          </div>
        )}
        <p className="mt-1 whitespace-pre-line text-sm leading-6 text-slate-700">
          {content.text}
        </p>
      </div>
    </div>
  )
}

function UnsupportedBlock({ block }) {
  if (block.content?.text) {
    return <LessonText content={block.content} />
  }

  return (
    <div className="rounded-lg border border-dashed border-slate-300 p-3 text-xs text-slate-500">
      Unsupported content block: {String(block.block_type)}
    </div>
  )
}

// Add new block types here; nothing else needs to change.
const BLOCK_COMPONENTS = {
  HEADING: LessonHeading,
  TEXT: LessonText,
  CODE: CodeBlock,
  TERMINAL_OUTPUT: TerminalOutput,
  CALLOUT: Callout,
}

export default function LessonBlocks({ blocks }) {
  const ordered = [...blocks].sort(
    (a, b) => (a.position ?? 0) - (b.position ?? 0),
  )

  return (
    <div className="space-y-5 rounded-2xl bg-white p-6 text-slate-700 shadow-sm ring-1 ring-slate-200 sm:p-8">
      {ordered.map((block, index) => {
        const Component =
          BLOCK_COMPONENTS[String(block.block_type || '').toUpperCase()]
        const key = block.id ?? index

        return Component ? (
          <Component key={key} content={block.content || {}} />
        ) : (
          <UnsupportedBlock key={key} block={block} />
        )
      })}
    </div>
  )
}
