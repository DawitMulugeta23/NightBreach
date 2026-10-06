import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import {
  Bell,
  BookOpen,
  ChevronDown,
  Flag,
  LayoutDashboard,
  Menu,
  Search,
  Settings,
  Target,
  TrendingUp,
  X,
} from 'lucide-react'
import { useState } from 'react'
import NightBreachLogo from '../components/common/NightBreachLogo.jsx'

const navigation = [
  { label: 'Dashboard', to: '/dashboard', icon: LayoutDashboard },
  { label: 'Learning Paths', to: '/learning', icon: BookOpen },
  { label: 'CTF Challenges', to: '/ctf', icon: Flag },
  { label: 'My Progress', to: '/progress', icon: TrendingUp },
  { label: 'Recommendations', to: '/recommendations', icon: Target },
]

function AppLayout() {
  const [mobileOpen, setMobileOpen] = useState(false)
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-[#020711] text-slate-100">
      <div className="flex min-h-screen">
        <aside className="hidden w-64 shrink-0 border-r border-[#112338] bg-[#030a13] lg:flex lg:flex-col">
          <div className="flex h-16 items-center border-b border-[#112338] px-5">
            <NightBreachLogo />
          </div>

          <nav className="nb-scrollbar flex-1 overflow-y-auto px-3 py-5">
            <div className="mb-2 px-3 text-[9px] font-bold uppercase tracking-[0.16em] text-slate-600">
              Main
            </div>

            <div className="space-y-1">
              {navigation.map(({ label, to, icon: Icon }) => (
                <NavLink
                  key={to}
                  to={to}
                  className={({ isActive }) =>
                    [
                      'group flex items-center gap-3 rounded-lg border px-3 py-2.5 text-sm transition',
                      isActive
                        ? 'border-blue-500/20 bg-blue-500/10 text-blue-300'
                        : 'border-transparent text-slate-500 hover:bg-slate-900/60 hover:text-slate-200',
                    ].join(' ')
                  }
                >
                  <Icon className="h-4 w-4" />
                  <span>{label}</span>
                </NavLink>
              ))}
            </div>

            <div className="my-5 border-t border-[#112338]" />

            <div className="mb-2 px-3 text-[9px] font-bold uppercase tracking-[0.16em] text-slate-600">
              Foundation Paths
            </div>

            <div className="space-y-1">
              {[
                ['Linux', 'blue'],
                ['Windows', 'blue'],
                ['Cyber Security', 'green'],
                ['Networking', 'cyan'],
                ['Offensive Security', 'red'],
                ['Defensive Security', 'orange'],
              ].map(([name, tone]) => (
                <button
                  key={name}
                  type="button"
                  onClick={() => navigate('/learning')}
                  className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-xs text-slate-500 transition hover:bg-slate-900/60 hover:text-slate-200"
                >
                  <span
                    className={[
                      'h-2 w-2 rounded-full',
                      tone === 'green' && 'bg-emerald-400',
                      tone === 'cyan' && 'bg-cyan-400',
                      tone === 'red' && 'bg-red-400',
                      tone === 'orange' && 'bg-orange-400',
                      tone === 'blue' && 'bg-blue-400',
                    ]
                      .filter(Boolean)
                      .join(' ')}
                  />
                  {name}
                </button>
              ))}
            </div>
          </nav>

          <div className="border-t border-[#112338] p-3">
            <NavLink
              to="/settings"
              className={({ isActive }) =>
                [
                  'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition',
                  isActive
                    ? 'bg-blue-500/10 text-blue-300'
                    : 'text-slate-500 hover:bg-slate-900/60 hover:text-slate-200',
                ].join(' ')
              }
            >
              <Settings className="h-4 w-4" />
              Settings
            </NavLink>
          </div>
        </aside>

        {mobileOpen && (
          <div className="fixed inset-0 z-50 lg:hidden">
            <button
              type="button"
              aria-label="Close navigation"
              onClick={() => setMobileOpen(false)}
              className="absolute inset-0 bg-black/70"
            />

            <aside className="relative flex h-full w-72 flex-col border-r border-[#17304b] bg-[#030a13] shadow-2xl">
              <div className="flex h-16 items-center justify-between border-b border-[#112338] px-5">
                <NightBreachLogo />
                <button
                  type="button"
                  onClick={() => setMobileOpen(false)}
                  className="text-slate-500 hover:text-white"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              <nav className="flex-1 p-3">
                {navigation.map(({ label, to, icon: Icon }) => (
                  <NavLink
                    key={to}
                    to={to}
                    onClick={() => setMobileOpen(false)}
                    className={({ isActive }) =>
                      [
                        'flex items-center gap-3 rounded-lg px-3 py-3 text-sm',
                        isActive
                          ? 'bg-blue-500/10 text-blue-300'
                          : 'text-slate-500 hover:bg-slate-900 hover:text-white',
                      ].join(' ')
                    }
                  >
                    <Icon className="h-4 w-4" />
                    {label}
                  </NavLink>
                ))}
              </nav>
            </aside>
          </div>
        )}

        <div className="flex min-w-0 flex-1 flex-col">
          <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b border-[#112338] bg-[#020711]/95 px-4 backdrop-blur-xl lg:px-6">
            <button
              type="button"
              onClick={() => setMobileOpen(true)}
              className="rounded-lg p-2 text-slate-500 hover:bg-slate-900 hover:text-white lg:hidden"
            >
              <Menu className="h-5 w-5" />
            </button>

            <div className="relative hidden max-w-xl flex-1 md:block">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-600" />
              <input
                className="nb-input h-9 w-full rounded-lg pl-9 pr-20 text-xs"
                placeholder="Search learning paths, rooms, lessons..."
              />
              <span className="absolute right-2 top-1/2 -translate-y-1/2 rounded border border-slate-800 px-1.5 py-0.5 text-[9px] text-slate-600">
                Ctrl + K
              </span>
            </div>

            <div className="ml-auto flex items-center gap-3">
              <div className="hidden items-center gap-1.5 text-xs text-slate-500 sm:flex">
                <span className="text-orange-400">◈</span>
                1,250
              </div>

              <button
                type="button"
                className="relative rounded-lg p-2 text-slate-500 hover:bg-slate-900 hover:text-white"
              >
                <Bell className="h-4 w-4" />
                <span className="absolute right-1 top-1 h-1.5 w-1.5 rounded-full bg-red-500" />
              </button>

              <button
                type="button"
                className="flex items-center gap-2 rounded-lg px-1.5 py-1 hover:bg-slate-900"
              >
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-xs font-bold">
                  L
                </div>
                <div className="hidden text-left sm:block">
                  <div className="text-xs font-semibold text-slate-200">
                    Learner
                  </div>
                  <div className="text-[10px] text-slate-600">Free Plan</div>
                </div>
                <ChevronDown className="hidden h-3.5 w-3.5 text-slate-600 sm:block" />
              </button>
            </div>
          </header>

          <main className="nb-scrollbar flex-1 overflow-x-hidden">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  )
}

export default AppLayout
