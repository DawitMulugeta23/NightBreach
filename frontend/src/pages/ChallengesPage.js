import { createNavbar } from '../components/Navbar.js';
import { createFooter } from '../components/Footer.js';

export function createChallengesPage() {
  const page = document.createElement('div');
  page.id = 'challenges-screen';
  page.className = 'hidden min-h-screen bg-neutral-950 text-neutral-100';
  
  const content = `
    <div class="w-full px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 py-8 md:py-12">
      <h1 class="text-xl md:text-2xl lg:text-3xl font-bold text-white mb-2">CHALLENGES</h1>
      <p class="text-sm text-neutral-400 mb-8 md:mb-10">Test your skills with hands-on cybersecurity challenges.</p>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
        <div class="group p-6 md:p-8 rounded-2xl bg-neutral-900/80 border border-neutral-800 hover:border-emerald-500/50 transition-all duration-300 hover:shadow-xl hover:shadow-emerald-500/5 hover:-translate-y-1">
          <div class="text-xs font-bold text-emerald-400 mb-2">TIER 1</div>
          <h3 class="text-lg font-bold text-white mb-2">Entry Level Practice</h3>
          <p class="text-sm text-neutral-400 mb-6">Approx. 50 levels</p>
          <button class="get-started-trigger w-full px-4 py-2.5 text-sm font-semibold rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white transition-all duration-200 shadow-lg shadow-emerald-600/20 hover:shadow-emerald-500/40">
            Enter Arena
          </button>
        </div>
        <div class="p-6 md:p-8 rounded-2xl bg-neutral-900/80 border border-neutral-800 opacity-60 cursor-not-allowed">
          <div class="text-xs font-bold text-neutral-500 mb-2">TIER 2</div>
          <h3 class="text-lg font-bold text-white mb-2">Intermediate Challenges</h3>
          <p class="text-sm text-neutral-400 mb-6">Approx. 50 levels</p>
          <button disabled class="w-full px-4 py-2.5 text-sm font-semibold rounded-xl bg-neutral-800 text-neutral-500 cursor-not-allowed">
            Coming Soon
          </button>
        </div>
        <div class="p-6 md:p-8 rounded-2xl bg-neutral-900/80 border border-neutral-800 opacity-60 cursor-not-allowed">
          <div class="text-xs font-bold text-neutral-500 mb-2">TIER 3</div>
          <h3 class="text-lg font-bold text-white mb-2">Advanced Pen-Test</h3>
          <p class="text-sm text-neutral-400 mb-6">Approx. 50 levels</p>
          <button disabled class="w-full px-4 py-2.5 text-sm font-semibold rounded-xl bg-neutral-800 text-neutral-500 cursor-not-allowed">
            Coming Soon
          </button>
        </div>
      </div>
    </div>
  `;
  
  page.appendChild(createNavbar('challenges'));
  page.insertAdjacentHTML('beforeend', content);
  page.appendChild(createFooter());
  
  return page;
}
