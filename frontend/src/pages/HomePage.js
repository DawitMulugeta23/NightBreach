import { createNavbar } from '../components/Navbar.js';
import { createFooter } from '../components/Footer.js';

export function createHomePage() {
  const page = document.createElement('div');
  page.id = 'landing-screen';
  page.className = 'min-h-screen bg-neutral-950 text-neutral-100';
  
  // Hero Section
  const heroHTML = `
    <div class="relative w-full px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 pt-12 md:pt-20 pb-10 md:pb-16 overflow-hidden">
      <img src="/ethioctf.jpeg" alt="Ethiopia Map" class="absolute -top-10 right-0 w-64 sm:w-80 md:w-96 lg:w-[450px] xl:w-[550px] opacity-20 pointer-events-none select-none" />
      <div class="relative max-w-4xl">
        <h1 class="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-extrabold leading-tight mb-4 text-white">
          NightBreach: ETHIOPIA'S PREMIER<br/>
          <span class="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-emerald-600">CYBER DEFENSE ACADEMY</span>
        </h1>
        <p class="text-neutral-400 text-sm md:text-base leading-relaxed max-w-2xl">
          Master Offensive & Defensive Security with Hands-On, Scenario-Based
          Training designed for Ethiopian Professionals.
        </p>
      </div>
    </div>
  `;
  
  // Cards Section
  const cardsHTML = `
    <div class="w-full px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 pb-12 md:pb-16">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
        ${['Beginners', 'Professionals', 'Enterprises'].map((type, i) => `
          <div class="group p-6 md:p-8 rounded-2xl bg-neutral-900/80 border border-neutral-800 hover:border-emerald-500/50 transition-all duration-300 hover:shadow-xl hover:shadow-emerald-500/5 hover:-translate-y-1">
            <div class="text-xs font-semibold uppercase tracking-wider text-emerald-400 mb-3">For ${type}</div>
            <h3 class="text-lg md:text-xl font-bold text-white mb-3">${['START YOUR CYBER JOURNEY', 'ADVANCE YOUR CAREER', "BUILD YOUR TEAM'S CAPABILITIES"][i]}</h3>
            <p class="text-sm text-neutral-400 mb-6 leading-relaxed">${[
              'No prior experience? Our foundational paths build your skills from the ground up.',
              'Deepen your expertise with specialized courses in Threat Intelligence, Incident Response, and Red Teaming.',
              'Custom training programs and team assessment tools to strengthen your security posture.'
            ][i]}</p>
            <button class="get-started-trigger w-full px-4 py-2.5 text-sm font-semibold rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white transition-all duration-200 shadow-lg shadow-emerald-600/20 hover:shadow-emerald-500/40">
              ${['EXPLORE FOUNDATIONS', 'VIEW ADVANCED PATHS', 'REQUEST DEMO'][i]}
            </button>
          </div>
        `).join('')}
      </div>
    </div>
  `;
  
  // What Sets Us Apart
  const featuresHTML = `
    <div class="relative w-full px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 py-12 md:py-16 overflow-hidden">
      <img src="/ethioctf.jpeg" alt="Ethiopia Map" class="absolute -left-32 top-1/2 -translate-y-1/2 w-80 sm:w-96 md:w-[450px] lg:w-[550px] opacity-10 pointer-events-none select-none" />
      <div class="relative">
        <h2 class="text-sm font-bold uppercase tracking-wider text-emerald-400 mb-8">WHAT SETS US APART</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
          ${[
            { icon: '🇪🇹', title: 'ETHIOPIAN CONTEXT', desc: 'Scenario-based labs reflecting local challenges' },
            { icon: '👨‍🏫', title: 'EXPERT MENTORSHIP', desc: 'Guidance from seasoned professionals' },
            { icon: '🛠️', title: 'HANDS-ON LEARNING', desc: 'Real-world tools and environments' }
          ].map(f => `
            <div class="p-6 md:p-8 rounded-2xl bg-neutral-900/80 border border-neutral-800 hover:border-emerald-500/30 transition-all duration-300 hover:shadow-lg hover:shadow-emerald-500/5">
              <div class="text-4xl md:text-5xl mb-4">${f.icon}</div>
              <h3 class="text-lg font-bold text-white mb-2">${f.title}</h3>
              <p class="text-sm text-neutral-400 leading-relaxed">${f.desc}</p>
            </div>
          `).join('')}
        </div>
      </div>
    </div>
  `;
  
  // Testimonials
  const testimonialsHTML = `
    <div class="w-full px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 py-12 md:py-16">
      <h2 class="text-sm font-bold uppercase tracking-wider text-neutral-400 mb-8">TESTIMONIALS</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
        <div class="p-6 md:p-8 rounded-2xl bg-neutral-900/80 border border-neutral-800">
          <p class="text-sm md:text-base text-neutral-300 mb-4 leading-relaxed">"The hands-on labs helped me understand real-world security challenges in Ethiopia."</p>
          <div class="text-xs text-neutral-500">— Debre Birhan University</div>
        </div>
        <div class="p-6 md:p-8 rounded-2xl bg-neutral-900/80 border border-neutral-800">
          <p class="text-sm md:text-base text-neutral-300 mb-4 leading-relaxed">"NightBreach transformed our cybersecurity curriculum with practical training."</p>
          <div class="text-xs text-neutral-500">— Addis Ababa Institute of Technology</div>
        </div>
      </div>
    </div>
  `;
  
  // Partners
  const partnersHTML = `
    <div class="w-full px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 py-8 md:py-12">
      <div class="flex flex-wrap items-center justify-center gap-6 md:gap-12">
        <span class="text-xs text-neutral-500 uppercase tracking-wider font-semibold">PARTNERSHIPS</span>
        <span class="text-sm font-bold text-neutral-300">Debre Birhan</span>
        <span class="text-sm text-neutral-400">port</span>
        <span class="text-sm text-neutral-400">satisfieduser</span>
      </div>
    </div>
  `;
  
  // Footer Map
  const mapHTML = `
    <div class="relative h-32 md:h-40 overflow-hidden">
      <img src="/ethioctf.jpeg" alt="Ethiopia Map" class="absolute bottom-0 right-0 w-64 sm:w-80 md:w-[450px] lg:w-[550px] opacity-15 pointer-events-none select-none" />
    </div>
  `;
  
  page.appendChild(createNavbar('home'));
  page.insertAdjacentHTML('beforeend', heroHTML);
  page.insertAdjacentHTML('beforeend', cardsHTML);
  page.insertAdjacentHTML('beforeend', featuresHTML);
  page.insertAdjacentHTML('beforeend', testimonialsHTML);
  page.insertAdjacentHTML('beforeend', partnersHTML);
  page.insertAdjacentHTML('beforeend', mapHTML);
  page.appendChild(createFooter());
  
  return page;
}
