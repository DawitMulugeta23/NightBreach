import React, { createContext, useContext, useState, useEffect } from 'react'

const DEFAULTS = {
  terminalFontSize: 14,
  terminalFontFamily: 'Menlo, Monaco, "Courier New", monospace',
  terminalCursorStyle: 'block',   // block | bar | underline
  terminalCursorBlink: true,
  terminalScrollback: 5000,
}

const STORAGE_KEY = 'roha_preferences'

const PreferencesContext = createContext(null)

export function PreferencesProvider({ children }) {
  const [prefs, setPrefs] = useState(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      return raw ? { ...DEFAULTS, ...JSON.parse(raw) } : DEFAULTS
    } catch {
      return DEFAULTS
    }
  })

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(prefs))
  }, [prefs])

  const updatePref = (key, value) => setPrefs((p) => ({ ...p, [key]: value }))
  const resetPrefs = () => setPrefs(DEFAULTS)

  return (
    <PreferencesContext.Provider value={{ prefs, updatePref, resetPrefs, defaults: DEFAULTS }}>
      {children}
    </PreferencesContext.Provider>
  )
}

export function usePreferences() {
  const ctx = useContext(PreferencesContext)
  if (!ctx) throw new Error('usePreferences must be used within PreferencesProvider')
  return ctx
}
