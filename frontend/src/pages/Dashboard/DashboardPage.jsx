import {
  ArrowRight,
  Clock3,
  Flame,
  Play,
  Trophy,
} from 'lucide-react'

import MetricCard from '../../components/common/MetricCard.jsx'
import ProgressBar from '../../components/common/ProgressBar.jsx'
import SectionHeader from '../../components/common/SectionHeader.jsx'
import StatusBadge from '../../components/common/StatusBadge.jsx'
import nightbreachAssets from '../../config/nightbreachAssets.js'

const activity = [
  {
    title: 'Linux Fundamentals',
    type: 'Lesson',
    time: '2 hours ago',
    tone: 'green',
  },
  {
    title: 'Web Exploitation 101',
    type: 'CTF Challenge',
    time: '5 hours ago',
    tone: 'purple',
  },
  {
    title: 'Network Scanning',
    type: 'Practice',
    time: '1 day ago',
    tone: 'orange',
  },
]

const challenges = [
  {
    title: 'SQL Injection',
    level: 'Beginner',
    points: 100,
    color: 'green',
  },
  {
    title: 'Hidden Directory',
    level: 'Intermediate',
    points: 150,
    color: 'orange',
  },
  {
    title: 'Admin Panel',
    level: 'Advanced',
    points: 300,
    color: 'red',
  },
]

function DashboardPage() {
  return (
    <div className="nb-page nb-grid">
      <div className="mx-auto max-w-[1500px] px-4 py-6 sm:px-6 lg:px-8">

        {/* Header */}
        <div className="mb-7 flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <div className="nb-kicker">Cybersecurity learning platform</div>

            <h1 className="mt-2 text-2xl font-bold tracking-tight text-white sm:text-3xl">
              Dashboard
            </h1>

            <p className="mt-1 text-sm text-slate-500">
              Your NightBreach learning workspace.
            </p>
          </div>

          <div className="hidden items-center gap-3 sm:flex">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-blue-500/20 bg-blue-500/10">
              <img
                src={nightbreachAssets.branding.shield}
                alt=""
                className="h-6 w-6 object-contain"
              />
            </div>

            <div>
              <div className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-600">
                Current Mode
              </div>
              <div className="mt-0.5 text-xs font-medium text-slate-300">
                Learning Mode
              </div>
            </div>
          </div>
        </div>

        {/* Metrics */}
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <MetricCard
            icon={nightbreachAssets.icons.learningPaths}
            label="Learning Progress"
            value="45%"
            detail="12 modules completed"
            tone="blue"
          />

          <MetricCard
            icon={nightbreachAssets.icons.success}
            label="Completed Rooms"
            value="3 / 12"
            detail="Rooms completed"
            tone="green"
          />

          <MetricCard
            icon={nightbreachAssets.icons.captureTheFlag}
            label="CTF Challenges"
            value="2 / 8"
            detail="Challenges completed"
            tone="purple"
          />

          <MetricCard
            icon={Trophy}
            label="Total Points"
            value="1,250"
            detail="Keep building your score"
            tone="orange"
          />
        </div>

        {/* Learning + Activity */}
        <div className="mt-6 grid gap-5 xl:grid-cols-[1.6fr_1fr]">

          {/* Continue Learning */}
          <section className="nb-card rounded-xl p-5">
            <SectionHeader
              title="Continue Learning"
              description="Pick up where you left off."
              action={
                <button className="hidden items-center gap-1 text-xs text-blue-400 transition hover:text-blue-300 sm:flex">
                  View Learning Paths
                  <ArrowRight className="h-3.5 w-3.5" />
                </button>
              }
            />

            <div className="grid gap-4 md:grid-cols-2">

              {/* Cybersecurity */}
              <div className="group relative overflow-hidden rounded-xl border border-blue-500/20 bg-blue-500/[0.035] p-4 transition duration-200 hover:border-blue-400/30 hover:bg-blue-500/[0.055]">
                <div className="pointer-events-none absolute -right-8 -top-8 h-28 w-28 rounded-full bg-blue-500/10 blur-3xl" />

                <div className="relative flex items-start justify-between">
                  <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-blue-500/20 bg-blue-500/10">
                    <img
                      src={nightbreachAssets.icons.cyberSecurity}
                      alt=""
                      className="h-7 w-7 object-contain"
                    />
                  </div>

                  <StatusBadge tone="blue">
                    In Progress
                  </StatusBadge>
                </div>

                <div className="relative mt-4">
                  <div className="text-sm font-semibold text-white">
                    Introduction to Cybersecurity
                  </div>

                  <div className="mt-1 text-xs text-slate-500">
                    Module 1 · Lesson 1.1
                  </div>
                </div>

                <div className="relative mt-5">
                  <div className="mb-2 flex justify-between text-[10px] text-slate-500">
                    <span>Progress</span>
                    <span>45%</span>
                  </div>

                  <ProgressBar value={45} />
                </div>

                <button className="nb-button-primary relative mt-4 flex w-full items-center justify-center gap-2 rounded-lg px-3 py-2 text-xs font-semibold">
                  Continue
                  <ArrowRight className="h-3.5 w-3.5" />
                </button>
              </div>

              {/* Practice */}
              <div className="group relative overflow-hidden rounded-xl border border-purple-500/20 bg-purple-500/[0.035] p-4 transition duration-200 hover:border-purple-400/30 hover:bg-purple-500/[0.055]">
                <div className="pointer-events-none absolute -right-8 -top-8 h-28 w-28 rounded-full bg-purple-500/10 blur-3xl" />

                <div className="relative flex items-start justify-between">
                  <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-purple-500/20 bg-purple-500/10">
                    <img
                      src={nightbreachAssets.icons.terminal}
                      alt=""
                      className="h-7 w-7 object-contain"
                    />
                  </div>

                  <StatusBadge tone="purple">
                    Practice
                  </StatusBadge>
                </div>

                <div className="relative mt-4">
                  <div className="text-sm font-semibold text-white">
                    Network Scanning Basics
                  </div>

                  <div className="mt-1 text-xs text-slate-500">
                    Nmap · Guided Practice
                  </div>
                </div>

                <div className="relative mt-5">
                  <div className="mb-2 flex justify-between text-[10px] text-slate-500">
                    <span>Progress</span>
                    <span>40%</span>
                  </div>

                  <ProgressBar value={40} tone="purple" />
                </div>

                <button className="nb-button-secondary relative mt-4 flex w-full items-center justify-center gap-2 rounded-lg px-3 py-2 text-xs font-semibold">
                  Resume Practice
                  <Play className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          </section>

          {/* Activity */}
          <section className="nb-card rounded-xl p-5">
            <SectionHeader title="Recent Activity" />

            <div className="space-y-1">
              {activity.map((item) => (
                <div
                  key={item.title}
                  className="flex items-center gap-3 rounded-lg px-2 py-3 transition hover:bg-slate-900/50"
                >
                  <div
                    className={[
                      'h-2.5 w-2.5 shrink-0 rounded-full',
                      item.tone === 'green' && 'bg-emerald-400',
                      item.tone === 'purple' && 'bg-purple-400',
                      item.tone === 'orange' && 'bg-orange-400',
                    ]
                      .filter(Boolean)
                      .join(' ')}
                  />

                  <div className="min-w-0 flex-1">
                    <div className="truncate text-xs font-medium text-slate-300">
                      {item.title}
                    </div>

                    <div className="mt-0.5 text-[10px] text-slate-600">
                      {item.type}
                    </div>
                  </div>

                  <span className="shrink-0 text-[10px] text-slate-600">
                    {item.time}
                  </span>
                </div>
              ))}
            </div>
          </section>
        </div>

        {/* Challenges + Weekly Goal */}
        <div className="mt-6 grid gap-5 xl:grid-cols-[1.6fr_1fr]">

          {/* Challenges */}
          <section className="nb-card rounded-xl p-5">
            <SectionHeader
              title="Next Challenges"
              description="Practice your skills with real-world scenarios."
              action={
                <a
                  href="/ctf"
                  className="flex items-center gap-1 text-xs text-blue-400 transition hover:text-blue-300"
                >
                  View all
                  <ArrowRight className="h-3.5 w-3.5" />
                </a>
              }
            />

            <div className="space-y-2">
              {challenges.map((challenge) => (
                <div
                  key={challenge.title}
                  className="group flex items-center gap-4 rounded-lg border border-slate-800/80 bg-slate-950/30 p-3 transition hover:border-slate-700 hover:bg-slate-900/50"
                >
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-blue-500/15 bg-blue-500/10">
                    <img
                      src={nightbreachAssets.icons.flag}
                      alt=""
                      className="h-6 w-6 object-contain"
                    />
                  </div>

                  <div className="min-w-0 flex-1">
                    <div className="text-xs font-semibold text-slate-200">
                      {challenge.title}
                    </div>

                    <div className="mt-1 flex items-center gap-2">
                      <StatusBadge tone={challenge.color}>
                        {challenge.level}
                      </StatusBadge>

                      <span className="text-[10px] text-slate-600">
                        {challenge.points} points
                      </span>
                    </div>
                  </div>

                  <button className="nb-button-secondary rounded-md px-3 py-1.5 text-[10px] font-semibold">
                    Start
                  </button>
                </div>
              ))}
            </div>
          </section>

          {/* Weekly Goal */}
          <section className="nb-card relative overflow-hidden rounded-xl p-5">
            <div className="pointer-events-none absolute -right-12 -top-12 h-40 w-40 rounded-full bg-orange-500/5 blur-3xl" />

            <SectionHeader title="Weekly Goal" />

            <div className="relative flex items-center gap-4">
              <div className="relative flex h-16 w-16 shrink-0 items-center justify-center rounded-full border-4 border-blue-500/20 border-t-blue-400">
                <Flame className="h-5 w-5 text-orange-400" />
              </div>

              <div>
                <div className="text-xl font-bold text-white">
                  1,250 XP
                </div>

                <div className="mt-1 text-xs text-slate-500">
                  1,250 / 2,000 XP
                </div>
              </div>
            </div>

            <ProgressBar
              value={62.5}
              className="relative mt-5"
            />

            <div className="relative mt-4 flex items-center gap-2 text-[10px] text-slate-600">
              <Clock3 className="h-3.5 w-3.5" />
              Goal resets in 4 days
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}

export default DashboardPage
