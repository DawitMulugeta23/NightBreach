import { createNavbar } from '../components/Navbar.js';
import { createFooter } from '../components/Footer.js';

export function createLeaderboardPage() {
  const page = document.createElement('div');
  page.id = 'leaderboard-screen';
  page.className = 'hidden min-h-screen bg-neutral-950 text-neutral-100';
  
  const content = `
    <div class="w-full px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 py-8 md:py-12">
      <h1 class="text-xl md:text-2xl lg:text-3xl font-bold text-white mb-2">LEADERBOARD</h1>
      <p class="text-sm text-neutral-400 mb-8 md:mb-10">Top performers in the NightBreach community.</p>
      
      <div class="rounded-2xl bg-neutral-900/80 border border-neutral-800 overflow-hidden">
        <div class="grid grid-cols-4 gap-4 p-4 md:p-6 border-b border-neutral-800 text-xs font-semibold uppercase tracking-wider text-neutral-400">
          <div>Rank</div>
          <div>Username</div>
          <div>Levels Completed</div>
          <div>Score</div>
        </div>
        <div class="divide-y divide-neutral-800">
          ${[1,2,3].map(i => `
            <div class="grid grid-cols-4 gap-4 p-4 md:p-6 text-sm text-neutral-300 hover:bg-neutral-800/50 transition-colors">
              <div class="text-emerald-400 font-bold">#${i}</div>
              <div>Coming Soon</div>
              <div>0</div>
              <div>0</div>
            </div>
          `).join('')}
        </div>
      </div>
    </div>
  `;
  
  page.appendChild(createNavbar('leaderboard'));
  page.insertAdjacentHTML('beforeend', content);
  page.appendChild(createFooter());
  
  return page;
}
