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

  const area = document.createElement('textarea')
  area.value = text
  area.style.position = 'fixed'
  area.style.opacity = '0'
  document.body.appendChild(area)
  area.select()

  try {
    return document.execCommand('copy')
  } catch {
    return false
  } finally {
    document.body.removeChild(area)
  }
}

function LessonHeading({ content }) {
  const text = content.text || ''
  if (Number(content.level) >= 3) {
    return (
      <h3 className="pt-2 text-lg font-semibold text-white">{text}</h3>
    )
  }
  return (
    <h2 className="border-b border-slate-800/80 pb-2 pt-4 text-2xl font-bold text-white">
      {text}
    </h2>
  )
}

function LessonText({ content }) {
  return (
    <p className="whitespace-pre-line text-[15px] leading-7 text-slate-300">
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

  async function handleCopy() {
    if (await copyText(code)) {
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    }
  }

  return (
    <div className="overflow-hidden rounded-xl border border-slate-800 bg-[#030914]">
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
        {code.split('\n').map((line, index) => (
          <div key={index}>
            {isShell && (
              <span className="select-none text-slate-600">$ </span>
            )}
            {line}
          </div>
        ))}
      </pre>
    </div>
  )
}

function TerminalOutput({ content }) {
  return (
    <div className="overflow-hidden rounded-xl border border-slate-800 bg-black/60">
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
    box: 'border-blue-500/30 bg-blue-500/5',
    accent: 'text-blue-400',
  },
  tip: {
    icon: Lightbulb,
    box: 'border-emerald-500/30 bg-emerald-500/5',
    accent: 'text-emerald-400',
  },
  warning: {
    icon: TriangleAlert,
    box: 'border-orange-500/30 bg-orange-500/5',
    accent: 'text-orange-400',
  },
  info: {
    icon: Info,
    box: 'border-slate-700 bg-slate-800/20',
    accent: 'text-slate-300',
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
        <p className="mt-1 text-sm leading-6 text-slate-300">
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
    <div className="rounded-lg border border-dashed border-slate-800 p-3 text-xs text-slate-600">
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
    <div className="space-y-5">
      {ordered.map((block) => {
        const Component =
          BLOCK_COMPONENTS[String(block.block_type || '').toUpperCase()]

        return Component ? (
          <Component key={block.id} content={block.content || {}} />
        ) : (
          <UnsupportedBlock key={block.id} block={block} />
        )
      })}
    </div>
  )
}
