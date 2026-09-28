import { NavLink, Outlet } from 'react-router-dom'
import {
  BookOpen,
  Flag,
  LayoutDashboard,
  Settings,
  Shield,
  Target,
  TrendingUp,
} from 'lucide-react'

const navigation = [
  {
    label: 'Dashboard',
    to: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    label: 'Learning',
    to: '/learning',
    icon: BookOpen,
  },
  {
    label: 'CTF Challenges',
    to: '/ctf',
    icon: Flag,
  },
  {
    label: 'Progress',
    to: '/progress',
    icon: TrendingUp,
  },
  {
    label: 'Recommendations',
    to: '/recommendations',
    icon: Target,
  },
]

function AppLayout() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="flex min-h-screen">
        <aside className="hidden w-64 shrink-0 border-r border-slate-800 bg-slate-950 lg:flex lg:flex-col">
          <div className="flex h-16 items-center gap-3 border-b border-slate-800 px-6">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-600">
              <Shield className="h-5 w-5 text-white" />
            </div>

            <div>
              <div className="font-semibold tracking-tight">NightBreach</div>
              <div className="text-xs text-slate-500">Cybersecurity Platform</div>
            </div>
          </div>

          <nav className="flex-1 space-y-1 p-4">
            {navigation.map(({ label, to, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  [
                    'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition',
                    isActive
                      ? 'bg-blue-600/15 text-blue-400'
                      : 'text-slate-400 hover:bg-slate-900 hover:text-slate-100',
                  ].join(' ')
                }
              >
                <Icon className="h-4 w-4" />
                {label}
              </NavLink>
            ))}
          </nav>

          <div className="border-t border-slate-800 p-4">
            <NavLink
              to="/settings"
              className={({ isActive }) =>
                [
                  'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition',
                  isActive
                    ? 'bg-blue-600/15 text-blue-400'
                    : 'text-slate-400 hover:bg-slate-900 hover:text-slate-100',
                ].join(' ')
              }
            >
              <Settings className="h-4 w-4" />
              Settings
            </NavLink>
          </div>
        </aside>

        <div className="flex min-w-0 flex-1 flex-col">
          <header className="flex h-16 items-center justify-between border-b border-slate-800 px-6">
            <div className="text-sm text-slate-400">
              Cybersecurity Learning & Skill Development
            </div>

            <div className="flex items-center gap-3">
              <div className="hidden text-right sm:block">
                <div className="text-sm font-medium text-slate-200">
                  Learner
                </div>
                <div className="text-xs text-slate-500">
                  Free Plan
                </div>
              </div>

              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-800 text-sm font-medium">
                L
              </div>
            </div>
          </header>

          <main className="flex-1">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  )
}

export default AppLayout
