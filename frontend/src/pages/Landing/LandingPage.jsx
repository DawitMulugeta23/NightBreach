import { ArrowRight, BookOpen, Flag, Shield, Terminal } from 'lucide-react'
import { Link } from 'react-router-dom'

const features = [
  {
    icon: BookOpen,
    title: 'Learn',
    description:
      'Build cybersecurity knowledge through structured Learning Paths, Modules, Rooms, and Lessons.',
  },
  {
    icon: Terminal,
    title: 'Practice',
    description:
      'Apply concepts through practical tasks, tools, command-line work, and Guided CTF activities.',
  },
  {
    icon: Flag,
    title: 'Challenge',
    description:
      'Investigate real practical scenarios through Guided and Independent CTF challenges.',
  },
]

function LandingPage() {
  return (
    <main className="min-h-screen bg-slate-950">
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(37,99,235,0.15),transparent_40%)]" />

        <div className="relative mx-auto max-w-6xl px-6 py-24 lg:px-8 lg:py-32">
          <div className="max-w-3xl">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-blue-500/20 bg-blue-500/10 px-3 py-1.5 text-sm text-blue-400">
              <Shield className="h-4 w-4" />
              Cybersecurity Learning & Skill Development
            </div>

            <h1 className="text-5xl font-bold tracking-tight text-white sm:text-6xl lg:text-7xl">
              Learn cybersecurity.
              <span className="block text-blue-500">
                Prove what you can do.
              </span>
            </h1>

            <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-400">
              NightBreach connects structured learning with practical
              cybersecurity exercises, controlled environments, and CTF
              challenges.
            </p>

            <div className="mt-10 flex flex-wrap gap-4">
              <Link
                to="/dashboard"
                className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-3 font-medium text-white transition hover:bg-blue-500"
              >
                Enter NightBreach
                <ArrowRight className="h-4 w-4" />
              </Link>

              <Link
                to="/ctf"
                className="inline-flex items-center gap-2 rounded-lg border border-slate-700 px-5 py-3 font-medium text-slate-200 transition hover:border-slate-600 hover:bg-slate-900"
              >
                Explore Challenges
              </Link>
            </div>
          </div>
        </div>
      </section>

      <section className="border-t border-slate-800 bg-slate-950">
        <div className="mx-auto grid max-w-6xl gap-px bg-slate-800 md:grid-cols-3">
          {features.map(({ icon: Icon, title, description }) => (
            <article
              key={title}
              className="bg-slate-950 p-8"
            >
              <div className="mb-5 flex h-10 w-10 items-center justify-center rounded-lg bg-slate-900 text-blue-400">
                <Icon className="h-5 w-5" />
              </div>

              <h2 className="text-xl font-semibold text-white">
                {title}
              </h2>

              <p className="mt-3 leading-7 text-slate-400">
                {description}
              </p>
            </article>
          ))}
        </div>
      </section>

      <section className="border-t border-slate-800">
        <div className="mx-auto max-w-6xl px-6 py-16 lg:px-8">
          <p className="text-center text-sm font-medium uppercase tracking-widest text-slate-500">
            NightBreach learning model
          </p>

          <p className="mt-4 text-center text-xl text-slate-300">
            Learn → Practice → Challenge → Demonstrate Skill
          </p>
        </div>
      </section>
    </main>
  )
}

export default LandingPage
