import { createNavbar } from '../components/Navbar.js';
import { createFooter } from '../components/Footer.js';

export function createLearningPathsPage() {
  const page = document.createElement('div');
  page.id = 'learning-paths-screen';
  page.className = 'hidden min-h-screen bg-neutral-950 text-neutral-100';
  
  const paths = [
    { icon: '🐧', title: 'LINUX FUNDAMENTALS', desc: 'Master CLI navigation, file permissions, user management, and process control.' },
    { icon: '🌐', title: 'NETWORKING FUNDAMENTALS', desc: 'Understand TCP/IP, subnetting, VLANs, routing, and essential protocols.' },
    { icon: '🔒', title: 'FUNDAMENTAL CYBER SECURITY', desc: 'Core principles of information security, risk management, and threat landscapes.' },
    { icon: '🛡️', title: 'DEFENSIVE SECURITY', desc: 'Learn to detect, prevent, and mitigate attacks and harden systems.' },
    { icon: '⚔️', title: 'OFFENSIVE SECURITY', desc: 'Understand ethical hacking techniques, vulnerability exploitation, and post-exploitation.' },
    { icon: '💻', title: 'WEB APPLICATION HACKING & ADVANCED SCENARIOS', desc: 'Analyze and exploit OWASP Top 10 web vulnerabilities and tackle complex labs.' }
  ];
  
  const content = `
    <div class="relative w-full px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 py-8 md:py-12 overflow-hidden">
      <img src="/ethioctf.jpeg" alt="Ethiopia Map" class="absolute -top-10 right-0 w-64 sm:w-80 md:w-96 lg:w-[450px] opacity-10 pointer-events-none select-none" />
      <div class="relative">
        <h1 class="text-xl md:text-2xl lg:text-3xl font-bold text-white mb-2">NightBreach: COMPREHENSIVE ETHIOPIAN PENETRATION TESTING ACADEMY</h1>
        <p class="text-sm text-neutral-400 mb-8 md:mb-10">Structured, gradual progress curriculum for ethical hacking mastery.</p>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
          ${paths.map(p => `
            <div class="group p-5 md:p-6 rounded-2xl bg-neutral-900/80 border border-neutral-800 hover:border-emerald-500/50 transition-all duration-300 hover:shadow-xl hover:shadow-emerald-500/5">
              <div class="flex items-start gap-4">
                <div class="w-10 h-10 md:w-12 md:h-12 rounded-xl bg-emerald-500/20 flex items-center justify-center text-xl md:text-2xl text-emerald-400 flex-shrink-0">${p.icon}</div>
                <div class="flex-1">
                  <h3 class="font-bold text-white text-sm md:text-base mb-1">${p.title}</h3>
                  <p class="text-xs text-neutral-400 leading-relaxed mb-3">${p.desc}</p>
                  <button class="get-started-trigger px-4 py-1.5 text-xs font-semibold rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white transition-all duration-200">START MODULE</button>
                </div>
              </div>
            </div>
          `).join('')}
        </div>
        
        <div class="mt-8 md:mt-10 p-5 md:p-6 rounded-2xl bg-neutral-900/80 border border-neutral-800">
          <div class="flex flex-col md:flex-row items-center justify-between gap-3">
            <span class="text-sm text-white font-medium">Overall Penetration Testing Mastery: 4%</span>
            <div class="w-full md:w-48 h-2.5 bg-neutral-800 rounded-full overflow-hidden">
              <div class="h-full bg-gradient-to-r from-emerald-400 to-emerald-600 rounded-full transition-all duration-500" style="width: 4%"></div>
            </div>
          </div>
        </div>
        
        <div class="mt-6 text-center">
          <button class="px-6 md:px-8 py-3 text-sm font-medium rounded-xl bg-neutral-800 hover:bg-neutral-700 text-neutral-300 transition-all duration-200 hover:shadow-lg hover:shadow-neutral-800/20">
            BROWSE PENTEST TOOLKIT & LEARNING CATALOG
          </button>
        </div>
      </div>
    </div>
  `;
  
  page.appendChild(createNavbar('paths'));
  page.insertAdjacentHTML('beforeend', content);
  page.appendChild(createFooter());
  
  return page;
}
