import {
  ArrowRight,
  Flag,
  LockKeyhole,
  Play,
  Shield,
  Trophy,
  Users,
  Zap,
} from 'lucide-react'

import MetricCard from '../../components/common/MetricCard.jsx'
import StatusBadge from '../../components/common/StatusBadge.jsx'
import SectionHeader from '../../components/common/SectionHeader.jsx'

const challenges = [
  {
    title: 'Byte Wizardry',
    description: 'A beginner friendly CTF to test your basics and enumeration skills.',
    difficulty: 'Beginner',
    players: 1243,
    points: 50,
    tone: 'green',
  },
  {
    title: 'Web Exploitation 101',
    description: 'Test your web hacking skills with SQLi, XSS, LFI and more.',
    difficulty: 'Intermediate',
    players: 987,
    points: 100,
    tone: 'purple',
  },
  {
    title: 'Rooted Reality',
    description: 'Privilege escalation and post-exploitation challenges await.',
    difficulty: 'Advanced',
    players: 654,
    points: 250,
    tone: 'red',
  },
]

function CTFPage() {
  return (
    <div className="nb-page">
      <div className="mx-auto max-w-[1500px] px-4 py-6 sm:px-6 lg:px-8">
        <div className="mb-7">
          <div className="flex items-start gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-500/10 text-blue-400">
              <Flag className="h-5 w-5" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white">
                Capture the Flag
              </h1>
              <p className="mt-1 text-sm text-slate-500">
                Compete, hack and climb the ranks.
              </p>
            </div>
          </div>
        </div>

        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <MetricCard icon={Flag} label="CTF Events" value="12" detail="Active" />
          <MetricCard
            icon={Trophy}
            label="Total Points"
            value="1,250"
            detail="Rank #842"
            tone="purple"
          />
          <MetricCard
            icon={Zap}
            label="Challenges Solved"
            value="48"
            detail="Across all events"
            tone="green"
          />
          <MetricCard
            icon={Users}
            label="Global Rank"
            value="842"
            detail="Top 12%"
            tone="orange"
          />
        </div>

        <div className="mt-6 grid gap-5 xl:grid-cols-[1fr_290px]">
          <main>
            <SectionHeader
              title="Active CTF Events"
              description="Challenges currently available to you."
            />

            <div className="grid gap-4 lg:grid-cols-3">
              {challenges.map((challenge) => (
                <article
                  key={challenge.title}
                  className="nb-card nb-card-hover overflow-hidden rounded-xl"
                >
                  <div className="relative h-36 overflow-hidden bg-gradient-to-br from-blue-950 via-slate-950 to-purple-950">
                    <div className="absolute inset-0 opacity-30">
                      <div className="absolute left-10 top-8 h-24 w-24 rounded-full border border-blue-400/40" />
                      <div className="absolute left-16 top-14 h-12 w-12 rounded-lg border border-cyan-400/30 rotate-45" />
                    </div>

                    <div className="absolute left-4 top-4">
                      <StatusBadge tone="green">LIVE</StatusBadge>
                    </div>

                    <div className="absolute bottom-4 left-4 flex h-11 w-11 items-center justify-center rounded-xl bg-black/30 text-blue-300">
                      <Shield className="h-6 w-6" />
                    </div>
                  </div>

                  <div className="p-4">
                    <h3 className="text-sm font-semibold text-white">
                      {challenge.title}
                    </h3>
                    <p className="mt-2 min-h-10 text-xs leading-5 text-slate-500">
                      {challenge.description}
                    </p>

                    <div className="mt-4 flex items-center justify-between text-[10px] text-slate-600">
                      <span>{challenge.players} Players</span>
                      <span>{challenge.points} pts</span>
                    </div>

                    <div className="mt-3 flex items-center justify-between">
                      <StatusBadge tone={challenge.tone}>
                        {challenge.difficulty}
                      </StatusBadge>

                      <button className="nb-button-primary flex items-center gap-1.5 rounded-md px-3 py-1.5 text-[10px] font-semibold">
                        Play Now <Play className="h-3 w-3" />
                      </button>
                    </div>
                  </div>
                </article>
              ))}
            </div>

            <div className="mt-6">
              <SectionHeader
                title="Featured Challenges"
                action={
                  <button className="flex items-center gap-1 text-xs text-blue-400">
                    View All <ArrowRight className="h-3.5 w-3.5" />
                  </button>
                }
              />

              <div className="nb-card overflow-hidden rounded-xl">
                {[
                  ['Warm Up', 'General', '50', 'Easy', 'green'],
                  ['Scan Me', 'Recon', '100', 'Easy', 'green'],
                  ['Hidden Directory', 'Web', '150', 'Medium', 'orange'],
                  ['SQL Detective', 'Web', '250', 'Medium', 'orange'],
                  ['Admin Panel', 'Web', '300', 'Hard', 'red'],
                ].map(([title, category, points, difficulty, tone]) => (
                  <div
                    key={title}
                    className="grid grid-cols-[1fr_100px_80px_90px] items-center gap-3 border-b border-slate-800/70 px-4 py-3 last:border-0"
                  >
                    <div className="flex items-center gap-3">
                      <Flag className="h-3.5 w-3.5 text-blue-400" />
                      <span className="text-xs text-slate-300">{title}</span>
                    </div>
                    <span className="text-[10px] text-slate-600">{category}</span>
                    <span className="text-[10px] text-slate-500">{points}</span>
                    <StatusBadge tone={tone}>{difficulty}</StatusBadge>
                  </div>
                ))}
              </div>
            </div>
          </main>

          <aside className="space-y-4">
            <div className="nb-card rounded-xl p-5">
              <SectionHeader title="Top Players" />

              <div className="space-y-2">
                {[
                  ['1', 'h4x0r_m4n', '5230'],
                  ['2', 'CyberGhost', '4987'],
                  ['3', '0xNinja', '4721'],
                  ['4', 'root_master', '4510'],
                  ['5', 'pwn_queen', '4322'],
                ].map(([rank, name, score]) => (
                  <div
                    key={name}
                    className="flex items-center gap-3 rounded-lg px-2 py-2 hover:bg-slate-900"
                  >
                    <span className="w-4 text-center text-[10px] text-slate-600">
                      {rank}
                    </span>
                    <div className="h-6 w-6 rounded-full bg-slate-800" />
                    <span className="flex-1 text-[10px] text-slate-300">{name}</span>
                    <span className="text-[10px] text-slate-500">{score}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="nb-card rounded-xl p-5">
              <div className="flex items-center gap-3">
                <LockKeyhole className="h-5 w-5 text-blue-400" />
                <div>
                  <div className="text-sm font-semibold text-white">CTF Guide</div>
                  <div className="text-[10px] text-slate-600">
                    Learn the basics
                  </div>
                </div>
              </div>

              <p className="mt-3 text-xs leading-5 text-slate-500">
                New to CTFs? Learn the basics and improve your skills with
                guided challenges.
              </p>

              <button className="nb-button-secondary mt-4 flex w-full items-center justify-center gap-2 rounded-lg px-3 py-2 text-xs font-semibold">
                View Guide <ArrowRight className="h-3.5 w-3.5" />
              </button>
            </div>
          </aside>
        </div>
      </div>
    </div>
  )
}

export default CTFPage
