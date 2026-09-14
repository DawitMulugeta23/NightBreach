import React from 'react'
import toast from 'react-hot-toast'
import { useAuth } from '../context/AuthContext'
import { useTheme } from '../context/ThemeContext'
import { usePreferences } from '../context/PreferencesContext'

const FONT_FAMILIES = [
  { label: 'Menlo / Monaco (default)', value: 'Menlo, Monaco, "Courier New", monospace' },
  { label: 'Consolas', value: 'Consolas, "Courier New", monospace' },
  { label: 'Fira Code', value: '"Fira Code", monospace' },
  { label: 'JetBrains Mono', value: '"JetBrains Mono", monospace' },
  { label: 'System UI', value: 'system-ui, monospace' },
]

function Section({ title, children }) {
  return (
    <div className="mt-6 p-6 rounded-2xl bg-neutral-50 dark:bg-neutral-900/80 border border-neutral-200 dark:border-neutral-800">
      <h2 className="text-sm font-bold uppercase tracking-wider text-emerald-400 mb-5">
        {title}
      </h2>
      <div className="space-y-5">{children}</div>
    </div>
  )
}

function Row({ label, hint, children }) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 sm:gap-6">
      <div className="min-w-0">
        <p className="text-sm font-semibold text-neutral-900 dark:text-white">{label}</p>
        {hint && (
          <p className="text-xs text-neutral-600 dark:text-neutral-400 mt-0.5">{hint}</p>
        )}
      </div>
      <div className="flex-shrink-0">{children}</div>
    </div>
  )
}

function Settings() {
  const { user } = useAuth()
  const { isDark, toggleTheme } = useTheme()
  const { prefs, updatePref, resetPrefs } = usePreferences()

  const controlClass =
    'px-3 py-2 text-xs font-semibold rounded bg-neutral-100 dark:bg-neutral-800 hover:bg-neutral-200 dark:hover:bg-neutral-700 border border-neutral-300 dark:border-neutral-700 text-neutral-900 dark:text-white cursor-pointer transition-colors'

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 md:px-8 lg:px-12 py-12">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl md:text-3xl font-bold text-neutral-900 dark:text-white">
          Settings
        </h1>
        <button
          onClick={() => { resetPrefs(); toast.success('Preferences reset') }}
          className="text-xs font-semibold uppercase tracking-wide text-neutral-600 dark:text-neutral-400 hover:text-red-400 transition-colors"
        >
          Reset to defaults
        </button>
      </div>

      <Section title="Account">
        <Row label="Username">
          <span className="text-sm font-semibold text-neutral-900 dark:text-white">
            {user?.username}
          </span>
        </Row>
        <Row label="Email">
          <span className="text-sm font-semibold text-neutral-900 dark:text-white">
            {user?.email || '—'}
          </span>
        </Row>
      </Section>

      <Section title="Appearance">
        <Row label="Theme" hint="Applies across the whole app immediately.">
          <button onClick={toggleTheme} className={controlClass + ' flex items-center gap-2'}>
            <i className={`fas ${isDark ? 'fa-sun text-yellow-400' : 'fa-moon text-neutral-600'}`}></i>
            {isDark ? 'Dark' : 'Light'}
          </button>
        </Row>
      </Section>

      <Section title="Terminal">
        <Row label="Font size" hint={`${prefs.terminalFontSize}px — applies to new terminals.`}>
          <div className="flex items-center gap-3">
            <input
              type="range"
              min="10"
              max="24"
              step="1"
              value={prefs.terminalFontSize}
              onChange={(e) => updatePref('terminalFontSize', Number(e.target.value))}
              className="w-40 accent-emerald-500"
            />
            <span className="text-sm font-mono text-neutral-900 dark:text-white w-8 text-right">
              {prefs.terminalFontSize}
            </span>
          </div>
        </Row>

        <Row label="Font family">
          <select
            value={prefs.terminalFontFamily}
            onChange={(e) => updatePref('terminalFontFamily', e.target.value)}
            className="px-3 py-2 text-xs rounded bg-neutral-100 dark:bg-neutral-800 border border-neutral-300 dark:border-neutral-700 text-neutral-900 dark:text-white cursor-pointer"
          >
            {FONT_FAMILIES.map((f) => (
              <option key={f.value} value={f.value}>{f.label}</option>
            ))}
          </select>
        </Row>

        <Row label="Cursor style">
          <div className="flex gap-2">
            {['block', 'bar', 'underline'].map((style) => (
              <button
                key={style}
                onClick={() => updatePref('terminalCursorStyle', style)}
                className={`px-3 py-2 text-xs font-semibold rounded border cursor-pointer transition-colors capitalize ${
                  prefs.terminalCursorStyle === style
                    ? 'bg-emerald-600 border-emerald-600 text-white'
                    : 'bg-neutral-100 dark:bg-neutral-800 border-neutral-300 dark:border-neutral-700 text-neutral-900 dark:text-white hover:bg-neutral-200 dark:hover:bg-neutral-700'
                }`}
              >
                {style}
              </button>
            ))}
          </div>
        </Row>

        <Row label="Cursor blink">
          <button
            onClick={() => updatePref('terminalCursorBlink', !prefs.terminalCursorBlink)}
            className={`relative w-12 h-6 rounded-full transition-colors cursor-pointer ${
              prefs.terminalCursorBlink ? 'bg-emerald-600' : 'bg-neutral-300 dark:bg-neutral-700'
            }`}
            aria-pressed={prefs.terminalCursorBlink}
          >
            <span
              className={`absolute top-0.5 w-5 h-5 rounded-full bg-white transition-transform ${
                prefs.terminalCursorBlink ? 'translate-x-6' : 'translate-x-0.5'
              }`}
            />
          </button>
        </Row>

        <Row label="Scrollback lines" hint="How much history the terminal keeps in memory.">
          <select
            value={prefs.terminalScrollback}
            onChange={(e) => updatePref('terminalScrollback', Number(e.target.value))}
            className="px-3 py-2 text-xs rounded bg-neutral-100 dark:bg-neutral-800 border border-neutral-300 dark:border-neutral-700 text-neutral-900 dark:text-white cursor-pointer"
          >
            {[1000, 2500, 5000, 10000, 25000].map((n) => (
              <option key={n} value={n}>{n.toLocaleString()}</option>
            ))}
          </select>
        </Row>
      </Section>
    </div>
  )
}

export default Settings
