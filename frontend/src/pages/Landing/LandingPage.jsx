import { ArrowRight, BookOpen, Flag, Shield, Terminal } from 'lucide-react'
import { Link } from 'react-router-dom'

import NightBreachLogo from '../../components/common/NightBreachLogo.jsx'

function LandingPage() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-[#020711] text-white">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_30%,rgba(0,120,255,0.18),transparent_32%),radial-gradient(circle_at_15%_80%,rgba(0,200,255,0.06),transparent_25%)]" />
      <div className="absolute inset-0 nb-grid opacity-40" />

      <header className="relative z-10 flex h-16 items-center justify-between border-b border-[#112338] px-5 sm:px-8">
        <NightBreachLogo />
        <div className="flex items-center gap-2">
          <Link
            to="/login"
            className="nb-button-secondary rounded-lg px-3 py-2 text-xs font-semibold"
          >
            Login
          </Link>
          <Link
            to="/register"
            className="nb-button-primary rounded-lg px-3 py-2 text-xs font-semibold"
          >
            Get Started
          </Link>
        </div>
      </header>

      <main className="relative z-10 mx-auto max-w-6xl px-5 pb-16 pt-20 sm:px-8 lg:pt-28">
        <div className="grid items-center gap-14 lg:grid-cols-[1.1fr_0.9fr]">
          <div>
            <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-blue-500/20 bg-blue-500/5 px-3 py-1.5 text-[10px] font-semibold text-blue-300">
              <Shield className="h-3.5 w-3.5" />
              Cybersecurity Learning & Skill Development
            </div>

            <h1 className="max-w-3xl text-4xl font-black tracking-tight sm:text-6xl">
              Learn cybersecurity.
              <br />
              <span className="text-blue-400">Prove what you can do.</span>
            </h1>

            <p className="mt-6 max-w-2xl text-sm leading-7 text-slate-500 sm:text-base">
              NightBreach combines structured learning paths, practical
              environments, hands-on practice and CTF challenges into one
              cybersecurity skill-development platform.
            </p>

            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                to="/login"
                className="nb-button-primary flex items-center gap-2 rounded-lg px-5 py-3 text-sm font-semibold"
              >
                Enter NightBreach
                <ArrowRight className="h-4 w-4" />
              </Link>

              <Link
                to="/ctf"
                className="nb-button-secondary flex items-center gap-2 rounded-lg px-5 py-3 text-sm font-semibold"
              >
                Explore Challenges
                <Flag className="h-4 w-4" />
              </Link>
            </div>
          </div>

          <div className="relative">
            <div className="absolute inset-0 rounded-full bg-blue-500/10 blur-3xl" />
            <div className="relative mx-auto flex aspect-square max-w-md items-center justify-center rounded-full border border-blue-500/20 bg-gradient-to-br from-blue-500/10 via-transparent to-cyan-500/5">
              <div className="absolute inset-8 rounded-full border border-blue-500/10" />
              <div className="absolute inset-20 rounded-full border border-cyan-500/10" />
              <Shield className="h-32 w-32 text-blue-400/80 sm:h-44 sm:w-44" strokeWidth={1} />
            </div>
          </div>
        </div>

        <div className="mt-20 grid gap-4 md:grid-cols-3">
          {[
            [
              'Learn',
              'Build cybersecurity knowledge through structured learning paths, modules, rooms and lessons.',
              BookOpen,
            ],
            [
              'Practice',
              'Apply concepts through practical labs, controlled environments and guided practice.',
              Terminal,
            ],
            [
              'Challenge',
              'Test your skills through realistic scenarios and independent CTF challenges.',
              Flag,
            ],
          ].map(([title, description, Icon]) => (
            <div key={title} className="nb-card nb-card-hover rounded-xl p-5">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-500/10 text-blue-400">
                <Icon className="h-5 w-5" />
              </div>
              <h2 className="mt-4 text-sm font-semibold text-white">{title}</h2>
              <p className="mt-2 text-xs leading-6 text-slate-500">{description}</p>
            </div>
          ))}
        </div>

        <div className="mt-10 text-center text-[10px] font-semibold tracking-[0.22em] text-slate-700">
          LEARN → PRACTICE → CHALLENGE → DEMONSTRATE SKILL
        </div>
      </main>
    </div>
  )
}

export default LandingPage
