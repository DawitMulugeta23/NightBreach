import React from 'react'
import { Link } from 'react-router-dom'
import MapBackground from '../components/MapBackground'
import ActionButton from '../components/ActionButton'
import { useAuth } from '../context/AuthContext'

function Home() {
  const { isAuthenticated, user } = useAuth()

  const cards = [
    {
      tag: 'For Beginners',
      icon: 'fa-rocket',
      title: 'START YOUR CYBER JOURNEY',
      desc: 'No prior experience? Our foundational paths build your skills from the ground up.',
      btn: 'EXPLORE FOUNDATIONS',
      to: '/learning-paths',
    },
    {
      tag: 'For Professionals',
      icon: 'fa-arrow-trend-up',
      title: 'ADVANCE YOUR CAREER',
      desc: 'Deepen your expertise with specialized courses in Threat Intelligence, Incident Response, and Red Teaming.',
      btn: 'VIEW ADVANCED PATHS',
      to: '/learning-paths',
    },
    {
      tag: 'For Enterprises',
      icon: 'fa-users-gear',
      title: "BUILD YOUR TEAM'S CAPABILITIES",
      desc: 'Custom training programs and team assessment tools to strengthen your security posture.',
      btn: 'REQUEST DEMO',
      to: '/challenges',
    },
  ]

  const features = [
    { icon: 'fa-flag', title: 'ETHIOPIAN CONTEXT', desc: 'Scenario-based labs reflecting local challenges' },
    { icon: 'fa-chalkboard-user', title: 'EXPERT MENTORSHIP', desc: 'Guidance from seasoned professionals' },
    { icon: 'fa-laptop-code', title: 'HANDS-ON LEARNING', desc: 'Real-world tools and environments' },
  ]

  return (
    <div className="relative bg-white dark:bg-neutral-950">
      {/* Hero */}
      <section className="relative w-full px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 pt-16 md:pt-24 pb-12 md:pb-20 overflow-hidden min-h-[500px] md:min-h-[600px] flex items-center">
        <MapBackground position="top-right" opacity={25} />
        <div className="relative max-w-5xl z-10">
          {isAuthenticated && (
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 text-xs font-semibold mb-4">
              <i className="fas fa-check-circle"></i>
              Welcome back, {user?.username}
            </div>
          )}
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold mb-4 ml-2">
            <i className="fas fa-shield-halved"></i>
            Ethiopia's Premier Cyber Defense Academy
          </div>
          <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-extrabold leading-tight text-neutral-900 dark:text-white mb-4">
            NightBreach
          </h1>
          <p className="text-xl sm:text-2xl md:text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-emerald-600 mb-4">
            Master Offensive & Defensive Security
          </p>
          <p className="text-neutral-600 dark:text-neutral-400 text-sm md:text-base leading-relaxed max-w-2xl flex items-start gap-2">
            <i className="fas fa-location-dot text-emerald-400 mt-1"></i>
            Hands-on, scenario-based training designed for Ethiopian Professionals.
          </p>
        </div>
      </section>

      {/* Three Cards */}
      <section className="w-full px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 pb-16 md:pb-20">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 md:gap-6 max-w-7xl mx-auto">
          {cards.map((card, i) => (
            <div key={i} className="card">
              <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-emerald-400 mb-3">
                <i className={`fas ${card.icon}`}></i>
                {card.tag}
              </div>
              <h3 className="text-xl font-bold text-neutral-900 dark:text-white mb-3">{card.title}</h3>
              <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-6 leading-relaxed">{card.desc}</p>
              <ActionButton to={card.to}>{card.btn}</ActionButton>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="relative w-full px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 py-16 md:py-20 overflow-hidden border-y border-neutral-200 dark:border-neutral-800">
        <MapBackground position="center-left" opacity={10} />
        <div className="relative max-w-7xl mx-auto">
          <h2 className="section-title">
            <i className="fas fa-star mr-2"></i>WHAT SETS US APART
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5 md:gap-6">
            {features.map((f, i) => (
              <div key={i} className="p-6 md:p-8 rounded-2xl bg-neutral-50 dark:bg-neutral-900/80 border border-neutral-200 dark:border-neutral-800 text-center">
                <div className="w-16 h-16 mx-auto rounded-full bg-emerald-500/10 flex items-center justify-center mb-4">
                  <i className={`fas ${f.icon} text-2xl text-emerald-400`}></i>
                </div>
                <h3 className="text-lg font-bold text-neutral-900 dark:text-white mb-2">{f.title}</h3>
                <p className="text-sm text-neutral-600 dark:text-neutral-400 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="w-full px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 py-16 md:py-20">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-sm font-bold uppercase tracking-wider text-neutral-600 dark:text-neutral-400 mb-8">
            <i className="fas fa-quote-left mr-2"></i>TESTIMONIALS
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5 md:gap-6">
            {[1, 2].map((i) => (
              <div key={i} className="p-6 md:p-8 rounded-2xl bg-neutral-50 dark:bg-neutral-900/80 border border-neutral-200 dark:border-neutral-800">
                <i className="fas fa-quote-right text-emerald-400 text-2xl mb-3 opacity-50"></i>
                <p className="text-sm md:text-base text-neutral-300 mb-4 leading-relaxed">
                  "Satisfied user has sailed ayou keep to confirme duetostarteland teene"
                </p>
                <div className="text-xs text-neutral-500">
                  <i className="fas fa-university mr-2"></i>Debre Birhan University
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer map */}
      <div className="relative h-40 md:h-56 overflow-hidden">
        <MapBackground position="center-right" opacity={25} />
      </div>
    </div>
  )
}

export default Home
