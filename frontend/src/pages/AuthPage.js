export function createAuthPage() {
  const page = document.createElement('div');
  page.id = 'auth-screen';
  page.className = 'hidden min-h-screen bg-neutral-950 text-neutral-100 flex items-center justify-center px-4 py-14 relative overflow-hidden';
  
  page.innerHTML = `
    <img src="/ethioctf.jpeg" alt="Ethiopia Map" class="absolute left-0 top-1/2 -translate-y-1/2 w-80 sm:w-96 md:w-[450px] lg:w-[550px] opacity-15 pointer-events-none select-none" />
    <img src="/ethioctf.jpeg" alt="Ethiopia Map" class="absolute right-0 top-1/2 -translate-y-1/2 w-80 sm:w-96 md:w-[450px] lg:w-[550px] opacity-15 pointer-events-none select-none scale-x-[-1]" />
    
    <div class="relative w-full max-w-md">
      <div class="relative mx-auto mb-6 w-20 h-20 md:w-24 md:h-24 flex items-center justify-center">
        <div class="absolute inset-0 rounded-full bg-emerald-500/30 blur-2xl"></div>
        <svg class="relative w-14 h-14 md:w-20 md:h-20 text-emerald-400 drop-shadow-[0_0_20px_rgba(52,211,153,0.5)]" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 2l7 3v6c0 5-3.5 8.5-7 10-3.5-1.5-7-5-7-10V5l7-3z" />
          <rect x="9.25" y="11" width="5.5" height="4.5" rx="1"/>
          <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 11V9.5a1.5 1.5 0 013 0V11" />
        </svg>
      </div>
      <h1 class="text-center text-sm md:text-base font-bold uppercase tracking-wide mb-6 text-white">NightBreach: ETHIOPIAN CYBER DEFENSE NETWORK</h1>
      <p id="auth-error" class="text-center text-red-400 text-xs min-h-[20px] mb-2"></p>
      
      <div id="login-view">
        <h2 class="text-center text-emerald-400 font-bold uppercase tracking-widest text-2xl md:text-3xl mb-8">LOGIN</h2>
        <form id="login-form" class="space-y-5 bg-neutral-900/40 border border-neutral-800 rounded-2xl p-6 md:p-8 backdrop-blur-sm">
          <label class="flex items-center gap-3 border-b border-neutral-700 focus-within:border-emerald-400 pb-2 transition-colors">
            <svg class="w-4 h-4 text-neutral-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
            </svg>
            <input id="login-username" type="text" placeholder="Username" required class="w-full bg-transparent text-sm text-white placeholder-neutral-500 focus:outline-none" />
          </label>
          <label class="flex items-center gap-3 border-b border-neutral-700 focus-within:border-emerald-400 pb-2 transition-colors">
            <svg class="w-4 h-4 text-neutral-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
            </svg>
            <input id="login-password" type="password" placeholder="Password" required class="w-full bg-transparent text-sm text-white placeholder-neutral-500 focus:outline-none" />
          </label>
          <div class="flex items-center justify-between text-xs text-neutral-400">
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" class="accent-emerald-500" />
              Remember me
            </label>
            <a href="#" class="hover:text-emerald-400 transition-colors">Forgot Password?</a>
          </div>
          <button type="submit" class="w-full py-3 rounded-xl font-bold uppercase tracking-wide text-white bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-400 hover:to-emerald-500 transition-all duration-200 shadow-lg shadow-emerald-600/20 hover:shadow-emerald-500/40">
            LOGIN
          </button>
        </form>
        <div class="text-center text-xs text-neutral-400 mt-6 space-y-2">
          <div><a href="#" id="show-register-link" class="text-emerald-400 hover:text-emerald-300 transition-colors">Create an account</a></div>
          <div><a href="#" id="back-to-map-login" class="hover:text-neutral-200 transition-colors">Back to Network Map</a></div>
        </div>
      </div>
      
      <div id="register-view" class="hidden">
        <h2 class="text-center text-emerald-400 font-bold uppercase tracking-widest text-2xl md:text-3xl mb-8">REGISTER</h2>
        <form id="register-form" class="space-y-4 bg-neutral-900/40 border border-neutral-800 rounded-2xl p-6 md:p-8 backdrop-blur-sm">
          <label class="flex items-center gap-3 border-b border-neutral-700 focus-within:border-emerald-400 pb-2 transition-colors">
            <svg class="w-4 h-4 text-neutral-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
            </svg>
            <input id="register-username" type="text" placeholder="Username" required class="w-full bg-transparent text-sm text-white placeholder-neutral-500 focus:outline-none" />
          </label>
          <label class="flex items-center gap-3 border-b border-neutral-700 focus-within:border-emerald-400 pb-2 transition-colors">
            <svg class="w-4 h-4 text-neutral-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" />
            </svg>
            <input id="register-email" type="email" placeholder="Email Address" required class="w-full bg-transparent text-sm text-white placeholder-neutral-500 focus:outline-none" />
          </label>
          <label class="flex items-center gap-3 border-b border-neutral-700 focus-within:border-emerald-400 pb-2 transition-colors">
            <svg class="w-4 h-4 text-neutral-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
            </svg>
            <input id="register-password" type="password" placeholder="Password" required class="w-full bg-transparent text-sm text-white placeholder-neutral-500 focus:outline-none" />
          </label>
          <label class="flex items-center gap-3 border-b border-neutral-700 focus-within:border-emerald-400 pb-2 transition-colors">
            <svg class="w-4 h-4 text-neutral-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
            </svg>
            <input id="register-confirm-password" type="password" placeholder="Confirm Password" required class="w-full bg-transparent text-sm text-white placeholder-neutral-500 focus:outline-none" />
          </label>
          <label class="flex items-center gap-3 border-b border-neutral-700 focus-within:border-emerald-400 pb-2 transition-colors">
            <svg class="w-4 h-4 text-neutral-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 21h16.5M4.5 3h15M5.25 3v18m13.5-18v18M9 6.75h1.5m-1.5 3h1.5m-1.5 3h1.5m3-6H15m-1.5 3H15m-1.5 3H15M9 21v-3.375c0-.621.504-1.125 1.125-1.125h3.75c.621 0 1.125.504 1.125 1.125V21" />
            </svg>
            <input id="register-institution" type="text" placeholder="Ethiopian Institution/Affiliation" class="w-full bg-transparent text-sm text-white placeholder-neutral-500 focus:outline-none" />
          </label>
          <label class="flex items-start gap-2 text-xs text-neutral-400 pt-1 cursor-pointer">
            <input id="register-agree-tos" type="checkbox" required class="accent-emerald-500 mt-0.5" />
            <span>Agree to <a href="#" class="text-emerald-400 hover:text-emerald-300 transition-colors">Terms of Service</a></span>
          </label>
          <button type="submit" class="w-full py-3 rounded-xl font-bold uppercase tracking-wide text-white bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-400 hover:to-emerald-500 transition-all duration-200 shadow-lg shadow-emerald-600/20 hover:shadow-emerald-500/40">
            REGISTER
          </button>
        </form>
        <div class="text-center text-xs text-neutral-400 mt-6 space-y-2">
          <div>Already have an account? <a href="#" id="show-login-link" class="text-emerald-400 hover:text-emerald-300 transition-colors">Login</a></div>
          <div><a href="#" id="back-to-map-register" class="hover:text-neutral-200 transition-colors">Back to Network Map</a></div>
        </div>
      </div>
      
      <p class="text-center text-[11px] text-neutral-600 mt-8">Secure Infrastructure & Monitoring<br/>&copy; 2025 NightBreach</p>
    </div>
  `;
  
  return page;
}
