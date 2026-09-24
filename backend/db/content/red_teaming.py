"""Red Teaming — full course content (4 rooms, 16 lessons).

The adversary-simulation specialization: methodology and legal ground,
command-and-control design, persistence and lateral movement across the
estate, and what the blue team actually sees when you move.

Terminal-type questions use the sandbox (curl, history, chmod are
available); everything else is graded as text. Answer hashes are computed
at import time from the plaintext answers below (via
db.content.common._hash_answers), keeping this file auditable.
"""
from db.content.common import _hash_answers


def _q(order_index, difficulty, prompt, *answers, qtype="text", setup=None):
    return {
        "order_index": order_index,
        "question_type": qtype,
        "difficulty": difficulty,
        "prompt": prompt,
        "answer_hash": _hash_answers(list(answers)),
        "setup_script": setup,
    }


PATH = {
    'slug': 'red-teaming',
    'title': 'Red Teaming',
    'description': 'Adversary simulation: C2, persistence, lateral movement, and evading detection.',
    'icon': '/redteam.svg',
    'order_index': 8,
    'rooms': [
        # ------------------------------------------------------------------
        {
            'order_index': 1,
            'title': 'Red Team Methodology',
            'description': 'Objectives, threat emulation, rules of engagement, and OPSEC.',
            'lessons': [
                {
                    'order_index': 1,
                    'title': 'Pentest vs Red Team',
                    'blocks': [
                        {"type": "text", "heading": "Two Different Games", "body": "A penetration test is point-in-time: scan the scope, find the vulns, prove them, report them — typically over days, with the defender aware. A red team is goal-driven adversary simulation: achieve an objective (domain admin, the finance file, a ransomware-ready foothold) while remaining undetected — over weeks or months, with the defender NOT told. Same tools, different sport."},
                        {"type": "text", "heading": "Objectives Over Vulns", "body": "Red teams measure success by OBJECTIVES, not findings: 'reached the crown jewels in 12 days without detection.' A single unpatched box matters only as a step toward the goal. This reframing is why red teams happily chain three 'medium' findings an assessor would file separately — the chain is the point."},
                        {"type": "text", "heading": "Purple Is the Payoff", "body": "The engagement's real value surfaces in the purple phase: red replays each move while blue sits beside them watching the dashboards. Which detections fired, how long the hunt took, what telemetry was missing — measured, not assumed. A red team that never tells blue anything improved nobody; shared debriefs are where the money is earned."},
                        {"type": "text", "heading": "Scope Is Wide but Not Unlimited", "body": "Red-team scope commonly includes physical entry, phishing, and third parties — but always bounded by the same rules of engagement as any test (Room 2). 'Adversary simulation' does not mean 'whatever we feel like': every technique stays inside written authorization, and deconfliction channels stay open so nobody mistakes the exercise for the real thing."},
                        {"type": "practice", "command": "history | tail -5", "instructions": "Review your own recent commands — an operator's history is the first artifact a defender would read. Notice what YOUR activity already reveals."},
                    ],
                    'questions': [
                        _q(1, "easy", "Red teaming simulates a real what — a goal-driven, stealthy opponent? (one word)", "adversary", "attacker", "threat", "enemy"),
                        _q(2, "medium", "A point-in-time assessment that scans a defined scope for vulnerabilities is called what? (one or two words)", "penetration test", "pentest", "pen test", "pen test"),
                        _q(3, "medium", "The team color that works WITH defenders during an exercise to verify detections? (one word)", "purple"),
                        _q(4, "medium", "The metric measuring how long the blue team took to notice you — one phrase? (e.g. time to X)", "time to detect", "detection time", "mttd", "time to detection"),
                        _q(5, "easy", "An exercise that also tests badge cloning, tailgating, and pretext calls targets which vector? (one word)", "physical", "physical security", "social", "people"),
                        _q(6, "easy", "Run history (or press the Up arrow in the terminal) — which shell builtin prints your command history? (one word)", "history", qtype="terminal"),
                    ],
                },
                {
                    'order_index': 2,
                    'title': 'Rules of Engagement & Legal Ground',
                    'blocks': [
                        {"type": "text", "heading": "The Document That Keeps You Out of Prison", "body": "Rules of Engagement define: exact scope (IPs, domains, people), testing windows, permitted and forbidden techniques, data-handling rules, emergency contacts, and deconfliction procedure. It is signed before a single packet moves. 'The client said it was fine' is not a legal defense anywhere worth operating — written authorization is."},
                        {"type": "text", "heading": "The Laws", "body": "The US Computer Fraud and Abuse Act (CFAA) and the UK Computer Misuse Act criminalize unauthorized access — and authorization that is vague does not protect you. Most countries have equivalents, and they apply to YOU regardless of intent: 'I was just testing' is precisely what an unauthorized tester says. Scope creep — that interesting host just outside the boundary — is how testers become defendants."},
                        {"type": "text", "heading": "Bounties, Third Parties, and Cloud", "body": "Bug bounty platforms publish their own scope — testing outside it is unauthorized even on the same company's infrastructure. Third-party providers (your client's SaaS vendor) need their own permission; shared-responsibility clouds mean the provider's systems are never in scope implicitly. When in doubt: stop, ask, get the answer in writing."},
                        {"type": "text", "heading": "Mid-Engagement Discoveries", "body": "You stumble onto an out-of-scope host, or evidence of a REAL intruder: stop touching it, document what you saw, notify the client's contact immediately. Real attackers and test traffic look identical in logs — deconfliction exists so the SOC does not respond to you, and so you do not trample a live incident (or a law-enforcement investigation)."},
                        {"type": "practice", "command": "curl -I http://example.com", "instructions": "Even a harmless probe belongs to an engagement context. Before any real target: confirm scope, window, and contacts — then act, and log everything you do."},
                    ],
                    'questions': [
                        _q(1, "easy", "The signed document defining scope, timing, and permitted techniques: rules of what? (one word)", "engagement", "roe", "rules of engagement"),
                        _q(2, "easy", "Which US federal anti-hacking statute is cited in nearly every engagement letter? (four-letter acronym)", "cfaa"),
                        _q(3, "medium", "The UK's counterpart to the CFAA goes by which name? (one phrase)", "computer misuse act", "cma", "computer misuse law"),
                        _q(4, "medium", "Mid-test you find an out-of-scope system — the correct action? (one or two words)", "stop", "stop testing", "report", "report it", "ask", "notify"),
                        _q(5, "easy", "Performing security testing without explicit, written permission is a what? (one word)", "crime", "criminal", "illegal", "felony"),
                    ],
                },
                {
                    'order_index': 3,
                    'title': 'OPSEC for Attackers',
                    'blocks': [
                        {"type": "text", "heading": "OPSEC Is Not Paranoia", "body": "Operational security is the discipline of noticing what your actions reveal — to defenders first, to the target second. Every choice leaks: infrastructure registration dates, source IPs in logs, working hours, file artifacts, even the tools' default fingerprints. OPSEC is simply cataloguing those leaks and closing the ones you can."},
                        {"type": "text", "heading": "Infrastructure Hygiene", "body": "Dedicated VPS and domains per engagement — never personal accounts, never reused across clients. Callback IPs geolocated thoughtfully (a shell phoning home to an unusual country is an anomaly in itself). WHOIS records betray the operator: privacy-registration is standard. And a payload's first appearance in VirusTotal shares your sample with every defender — including the target's vendor."},
                        {"type": "text", "heading": "Payload and Artifact OPSEC", "body": "Scanning your own payload on VirusTotal before launch tells you what EDR sees — and tells the vendors too; hash-checking without uploading is the compromise. Default Metasploit payloads, unmodified user-agents, and predictable callback patterns are signatures as loud as any YARA rule. Customize: strings, sleep profiles, headers, and encryption all leave fingerprints."},
                        {"type": "text", "heading": "Human OPSEC", "body": "Activity patterns are telltale: bursts at 3 a.m. local time stand out when the operator's timezone says otherwise. Working hours inside the target's timezone, traffic that resembles the sites the target actually visits, and accounts created with realistic footprints — the human layer is where most operations burn, because tools were hardened and habits were not."},
                        {"type": "practice", "command": "history | tail -10", "instructions": "Audit your own trail: every command, timestamped. Now imagine a SOC analyst reading it — which lines would look suspicious even if harmless?"},
                    ],
                    'questions': [
                        _q(1, "easy", "Operational security — the four-letter abbreviation?", "opsec"),
                        _q(2, "medium", "Freshly registered callback domains are trivially flagged via which public record? (one word)", "whois", "registration", "registrar", "age"),
                        _q(3, "medium", "When a payload phones home from YOUR infrastructure and lands in defender logs, that infrastructure is now what? (one word)", "burned", "known", "exposed", "compromised", "identified"),
                        _q(4, "hard", "Forging file timestamps to blend artifacts into the timeline — one word?", "timestomping", "timestomp", "timestamp manipulation"),
                        _q(5, "medium", "The multi-engine file-scanning site attackers AND defenders both use — but submissions share samples with the blue team. Name it. (one or two words)", "virustotal", "virus total", "vt"),
                    ],
                },
                {
                    'order_index': 4,
                    'title': "Threat Intelligence & Adversary Emulation",
                    'blocks': [
                        {"type": "text", "heading": "MITRE ATT&CK: The Shared Language", "body": "ATT&CK organizes attacker behavior into tactics (the WHY — persistence, credential access, exfiltration) and techniques (the HOW — pass the hash, scheduled task), with procedures below them (the specific implementation a group uses). Every red-team plan, detection rule, and gap assessment now speaks this vocabulary — if you cannot map it to ATT&CK, you cannot discuss it professionally."},
                        {"type": "text", "heading": "From Intel to Emulation", "body": "Threat intelligence says who is likely to attack your sector and what they actually do: financially motivated crews (FIN7-style) versus nation-state groups (APT-tracked), each with preferred initial access, tooling, and living-off-the-land habits. Emulation means adopting a REAL group's TTPs — not their malware — so defenders rehearse against realistic behavior."},
                        {"type": "text", "heading": "IOCs vs TTPs", "body": "Indicators (hashes, IPs, domains) are cheap and rot fast — defenders block them within hours. TTPs are behavioral and durable: blocking 'credential dumping from LSASS' outlives any single sample. Intelligence work ranks accordingly: collect TTPs first, indicators as supporting evidence. Diamond model thinking (adversary, capability, infrastructure, victim) keeps attribution honest."},
                        {"type": "text", "heading": "Writing the Emulation Plan", "body": "Pick the group, pull its ATT&CK technique list, choose the subset matching your access and constraints, map each technique to objective milestones, and define what 'success' looks like for red AND what 'caught it' looks like for blue. The plan is a script both teams can score — ambiguity in an exercise is just unmeasured noise."},
                        {"type": "practice", "command": "curl -I http://example.com", "instructions": "Recon feeds intelligence: passive sources (DNS, certificates, breach forums) build the picture before engagement traffic ever starts."},
                    ],
                    'questions': [
                        _q(1, "easy", "The MITRE framework cataloguing attacker tactics and techniques — its name? (five letters, or ATT&CK)", "attack", "att&ck", "attck", "mitre attack", "mitre att&ck"),
                        _q(2, "medium", "In ATT&CK, the attacker's GOAL (persistence, exfiltration) lives at which level — tactic or technique? (one word)", "tactic", "tactics"),
                        _q(3, "medium", "APT-tracked groups acting on behalf of a country are classified as which actor type? (one phrase)", "nation-state", "state", "apt", "nation state", "state-sponsored"),
                        _q(4, "easy", "Adversary emulation focuses on copying a real group's what — the three-letter summary of behaviors? (acronym, plural)", "ttps", "ttp", "tactics"),
                        _q(5, "medium", "Static artifacts like hashes and IPs are called what, in contrast to behavioural TTPs? (acronym, plural)", "iocs", "ioc"),
                    ],
                },
            ],
        },
        # ------------------------------------------------------------------
        {
            'order_index': 2,
            'title': 'Command & Control',
            'description': 'C2 infrastructure, channels, and beaconing.',
            'lessons': [
                {
                    'order_index': 1,
                    'title': 'C2 Foundations',
                    'blocks': [
                        {"type": "text", "heading": "Why Not Just a Reverse Shell", "body": "A raw reverse shell is one connection that dies on network blips, offers no encryption, no task queue, no second operator. Command-and-control infrastructure wraps the channel in reliability (reconnect, retries), security (TLS, encryption at rest), and scale (many implants, many operators) — the difference between a demo and an operation."},
                        {"type": "text", "heading": "The Components", "body": "The implant runs on target. The C2 server holds tasking and loots. Listeners define protocols and ports. Profiles shape traffic. Redirectors sit between implant and server so a burned front door costs one box, not the whole operation. Operators interact through a teamserver while targets only ever see the redirector."},
                        {"type": "text", "heading": "Beaconing vs Interactive", "body": "Interactive (cobalt-strike style) shells trade commands fast — loud and exposed. Beaconing polls on an interval: check in, receive task, execute, report, sleep. Quiet and robust, at the price of latency. Mature operations run beacons by default and go interactive only for short, planned windows — usually where they get caught."},
                        {"type": "text", "heading": "Profiles Decide How You Look", "body": "Malleable C2 profiles rewrite beacon traffic to mimic real sites — headers, URIs, bodies, and callback patterns shaped to look like a jQuery CDN, a corporate login, or a health-check ping. Matching the traffic to what that network legitimately carries is the difference between blending in and becoming an anomaly in the proxy log."},
                        {"type": "practice", "command": "curl -I http://example.com", "instructions": "Study what a genuine web response looks like — headers, server tokens, caching directives. C2 traffic must imitate exactly this texture to blend."},
                    ],
                    'questions': [
                        _q(1, "easy", "The agent program running on the target that talks back to C2 — one word?", "implant", "beacon", "agent", "payload", "backdoor"),
                        _q(2, "easy", "The server infrastructure used to issue commands — spelled out in full? (e.g. command and control)", "command and control", "command & control", "c2", "c&c", "command and control"),
                        _q(3, "medium", "A configuration that reshapes beacon HTTP to mimic a legitimate site — named after what kind of profile? (one word)", "malleable", "malleable profile", "traffic profile", "profile"),
                        _q(4, "medium", "The quiet pattern of checking in on a fixed interval for tasking — one word?", "beaconing", "beacon", "heartbeat", "polling"),
                        _q(5, "hard", "The disposable front layer between beacons and the real C2 server, absorbing blame when burned — one word?", "redirector", "redirectors", "proxy", "proxies", "redirector server"),
                    ],
                },
                {
                    'order_index': 2,
                    'title': 'Transports & Channels',
                    'blocks': [
                        {"type": "text", "heading": "HTTP/HTTPS: The Default", "body": "Port 443 is open to the world, inspected by every proxy — which cuts both ways: your traffic flows, but its shape is visible. HTTPS hides content, not metadata: destinations, SNI, sizes, timing, JA3 fingerprints. C2 over 443 succeeds when its ENVELOPE matches ordinary web traffic — the encryption is the easy part."},
                        {"type": "text", "heading": "DNS: The Channel That Cannot Be Blocked", "body": "Every network needs DNS, and queries traverse firewalls almost untouched — making it the classic exfil and tasking channel. Encode data in subdomain labels (a1b2c3.evil.com) or TXT responses, point resolvers at your authoritative server, and the corporate resolver does the forwarding for you. Slow, but nearly impossible to block without breaking the network itself."},
                        {"type": "text", "heading": "DNS over HTTPS and Domain Fronting", "body": "DoH wraps DNS in TLS so local resolvers and split-DNS telemetry see only an encrypted stream to a DoH provider. Domain fronting hides the true destination inside an approved CDN connection: TLS SNI shows cloudflare.com, the inner HTTP header routes to the attacker's host. Fronting has been largely mitigated by CDNs — but its principle (hiding in permitted channels) recurs wherever trust is inherited."},
                        {"type": "text", "heading": "Choosing the Transport", "body": "Match the channel to the environment: HTTP(S) everywhere; DNS where egress is filtered but resolution works; DoH where plain DNS is monitored; fallback chains so losing one channel degrades operations instead of ending them. Red teams plan for channel failure — blue teams plan for it too, which is why egress filtering and DNS monitoring rank among the highest-value defenses."},
                        {"type": "practice", "command": "curl -s -o /dev/null -w '%{http_code} %{time_total}s\\n' http://example.com", "instructions": "Measure a plain HTTP round trip — the rhythm C2 traffic must imitate. Timing anomalies are what beacon detectors hunt first."},
                    ],
                    'questions': [
                        _q(1, "easy", "Which port, almost universally allowed out, makes it the default C2 transport? (number)", "443"),
                        _q(2, "medium", "Encoding commands and data inside subdomain labels to reach an attacker nameserver — name the channel. (one or two words)", "dns tunneling", "dns", "tunneling", "dns over udp"),
                        _q(3, "medium", "DNS queries wrapped in TLS so local resolvers cannot read them — three-letter acronym?", "doh", "dns over https", "doq"),
                        _q(4, "hard", "Hiding the true destination behind an approved CDN host, where TLS SNI shows the allowed domain — one phrase?", "domain fronting", "fronting"),
                        _q(5, "medium", "Why is DNS ideal for exfiltration? Because it is typically what through firewalls? (one word)", "allowed", "permitted", "open", "whitelisted", "accepted"),
                    ],
                },
                {
                    'order_index': 3,
                    'title': 'Beaconing & Evasion',
                    "blocks": [
                        {"type": "text", "heading": "Sleep, Jitter, Rhythm", "body": "Beacon sleep is the check-in interval; jitter is the randomization around it — 60 seconds with 30% jitter lands between 42 and 78 seconds. Fixed intervals scream: packet-timing graphs render them as perfect spikes visible to any network analyst. Jitter breaks the periodicity while keeping the channel responsive — the cheapest evasion in the toolkit."},
                        {"type": "text", "heading": "Looking Like the Neighborhood", "body": "Legitimate User-Agents (never the library default), URIs and headers copied from the site being mimicked, request/response sizes padded to resemble real pages, and a full request-response cycle rather than fire-and-forget pings. A proxy analyst's question is 'does this look like our traffic?' — the beacon's job is to be boring enough that the answer is yes."},
                        {"type": "text", "heading": "What Detection Sees", "body": "Beacon hunters plot connection timing, jitter, and session regularity — a human browses erratically; a beacon does not. JA3 fingerprints flag unusual TLS stacks; DNS analytics catch high-entropy subdomain chains; proxy logs correlate one host visiting one path on an odd domain every 60 seconds. The behaviors, not the payloads, are what give beacons away."},
                        {"type": "text", "heading": "Trade-offs", "body": "Longer sleeps and higher jitter mean quieter operations with slower tasking — interactives windows become precious. Short sleeps mean responsive control and a visible rhythm. Operators tune per environment and per phase: reconnaissance stays quiet; the final push to objectives may deliberately run hot, accepting detection risk for speed."},
                        {"type": "practice", "command": "for i in 1 2 3; do curl -s -o /dev/null -w '%{time_total}\\n' http://example.com; sleep 2; done", "instructions": "Generate a small timing series — the raw material of beacon analysis. Notice how human-driven timing (your sleep commands, network jitter) already varies."},
                    ],
                    'questions': [
                        _q(1, "easy", "Random variation added to beacon intervals to defeat periodicity detection — one word?", "jitter"),
                        _q(2, "easy", "The configured time between beacon check-ins — one word?", "sleep", "interval", "beacon interval"),
                        _q(3, "medium", "Hunting for inhumanly regular connection intervals in network data — two words?", "beacon analysis", "timing analysis", "periodicity analysis"),
                        _q(4, "medium", "The TLS ClientHello fingerprint used to flag unusual protocol stacks — three-letter acronym?", "ja3", "ja3s"),
                        _q(5, "medium", "Setting beacon sleep to zero for hands-on exploitation sacrifices which asset? (one word)", "stealth", "opsec", "privacy", "quiet", "discretion"),
                        _q(6, "easy", "The timing practice loop paused between requests — which command sleeps for N seconds? (one word)", "sleep", qtype="terminal"),
                    ],
                },
                {
                    'order_index': 4,
                    'title': 'C2 Infrastructure Hygiene',
                    'blocks': [
                        {"type": "text", "heading": "Build for Burning", "body": "Assume every front will be identified: domains get blocklisted, VPS providers respond to abuse reports, certificates expire into investigations. The operational answer is rotation — when a redirector burns, discard it and fail over to the next, never mourning or reusing it. Infrastructure is consumable; the pipeline that provisions replacement infrastructure is the asset."},
                        {"type": "text", "heading": "Compartmentalization", "body": "Engagement A's domains, servers, and payload hashes must never touch engagement B's — cross-contamination links clients together and creates legal and OPSEC nightmares. Separate accounts, separate providers where practical, separate key material. Compartment discipline is what lets an operator run multiple engagements without one burned domain unravelling all of them."},
                        {"type": "text", "heading": "Hiding the Origin", "body": "A CDN in front of the C2 origin hides the true server IP behind anycast edges — defenders see cloudflare.com, not your VPS. Certificate transparency logs publish every cert issued, so subdomains and issuance timing leak unless deliberately managed. Privacy-guarded registration and aged domains blunt the two fastest enrichment paths: WHOIS and creation-date checks."},
                        {"type": "text", "heading": "When It All Burns", "body": "Response to burned infrastructure is a rehearsed procedure, not improvisation: rotate channels, reissue payloads with new hashes and config, move operators to clean accounts, and preserve what defenders learned only in your own notes. The teams that rebuild fastest win — which is why mature operations treat their C2 build pipeline, not any single server, as the crown jewel."},
                        {"type": "practice", "command": "curl -I http://example.com", "instructions": "Read the response headers as a defender would: server tokens, redirects, edge identifiers. Everything exposed here is enrichment a hunter would run against your infrastructure."},
                    ],
                    'questions': [
                        _q(1, "medium", "A C2 domain lands on a blocklist — standard operator practice? (one word)", "burn", "rotate", "abandon", "replace", "discard"),
                        _q(2, "easy", "Public WHOIS records reveal the registrant's what? (one word)", "name", "identity", "information", "details", "address"),
                        _q(3, "medium", "Traffic fronted by Cloudflare or Akamai hides the origin server behind which three-letter technology? (acronym)", "cdn", "proxy", "reverse proxy"),
                        _q(4, "hard", "Keeping each engagement's infrastructure fully isolated from every other — one word?", "compartmentalization", "compartmentalisation", "segmentation", "isolation"),
                        _q(5, "easy", "True or false: reusing the same payload hash across engagements protects OPSEC, because defenders already know it. (true/false)", "false"),
                    ],
                },
            ],
        },
        # ------------------------------------------------------------------
        {
            'order_index': 3,
            'title': 'Persistence & Lateral Movement',
            'description': 'Staying in, moving sideways, and credential reuse across the estate.',
            'lessons': [
                {
                    'order_index': 1,
                    'title': 'Persistence on Linux',
                    'blocks': [
                        {"type": "text", "heading": "SSH Keys: Quiet and Durable", "body": "Append the attacker's public key to ~/.ssh/authorized_keys and access survives password rotation, account resets, and most monitoring — the single quietest persistence on Linux. Variants: a new key in another user's directory once you have root, or a command= restriction-free key slipped into a shared account. Detection lives in watching that file change."},
                        {"type": "text", "heading": "Scheduled and Startup Hooks", "body": "crontab entries (@reboot especially) re-run payloads on schedule; systemd units fire at boot or on timers; shell startup files (~/.bashrc, ~/.profile, /etc/profile.d/) execute on every login — nothing suspicious to a process monitor, just a line in a config file. As root, /etc/ld.so.preload injects a library into EVERY process, hiding files from ls itself."},
                        {"type": "text", "heading": "Choosing the Layer", "body": "Match persistence to your privileges and risk appetite: user-level (bashrc, user cron) survives but dies at logout cleanup and only covers that account; root-level (systemd, ld.so.preload, SUID binaries) survives reboots but leaves louder artifacts. Each choice trades durability against detectability — and against what incident response will wipe first."},
                        {"type": "text", "heading": "The Defender's View", "body": "Watch for: new keys in authorized_files (file-integrity monitoring), unexpected crontab modifications, new systemd units (systemd-run logs, unit-file changes), and ld.so.preload existing at all — on a healthy server that file is empty or absent. Persistence detection is mostly CONFIG monitoring, which is why attackers pivot to the channels defenders do not watch."},
                        {"type": "practice", "command": "mkdir -p ~/.ssh && chmod 700 ~/.ssh && ls -ld ~/.ssh", "instructions": "Create and inspect your own .ssh directory with its correct permissions — the same anatomy an attacker would stage a key inside."},
                    ],
                    'questions': [
                        _q(1, "easy", "Run: chmod 700 ~/.ssh — which octal mode did you just set on the directory? (number)", "700", qtype="terminal"),
                        _q(2, "easy", "Which file inside ~/.ssh lists the public keys allowed to log in? (filename)", "authorized_keys", ".ssh/authorized_keys", "authorized keys"),
                        _q(3, "medium", "Shell startup files like ~/.bashrc run on each what — making them a persistence goldmine? (one word)", "login", "session", "startup", "start", "shell"),
                        _q(4, "hard", "Which file, when populated, injects a shared library into every process on the system? (one path)", "/etc/ld.so.preload", "ld.so.preload", "/etc/ld.so.preload file"),
                        _q(5, "medium", "Boot-time persistence units in systemd live in which directory? (one path)", "/etc/systemd/system", "/lib/systemd/system", "systemd", "/etc/systemd"),
                    ],
                },
                {
                    'order_index': 2,
                    'title': 'Persistence on Windows',
                    'blocks': [
                        {"type": "text", "heading": "The Autostart Registry", "body": "HKCU and HKLM ...\\CurrentVersion\\Run entries execute at every logon — the textbook implant location, writable by the user for HKCU and by an admin for HKLM. Companion locations multiply the options: RunOnce, the Startup folder, Winlogon shell keys, and service DLL registration. Autoruns enumerates them all in one view; defenders watch the same list."},
                        {"type": "text", "heading": "Tasks, Services, and WMI", "body": "Scheduled tasks (schtasks /create) run with chosen credentials and triggers — SYSTEM-level persistence with a legitimate scheduler's face. Services (sc create) start at boot before anyone logs on. WMI permanent event subscriptions fire on timers or logon events with no obvious executable on disk. Each abuses a trusted Windows subsystem — which is exactly why they work."},
                        {"type": "text", "heading": "The Dwell-Time Lesson", "body": "Dwell time — how long intrusion stays undetected — is measured in months in real breaches, and persistence explains why: defenders hunt the initial intrusion, attackers settle into native channels. Once foothold survives reboots and credential resets, the operation shifts from exploitation to patience: quiet check-ins, waiting for the right moment."},
                        {"type": "text", "heading": "Detection Is Event-Log Deep", "body": "Windows logs this catalog: 4698 (task created), 7045 (service installed), registry writes to Run keys, new entries in Startup folders — each with a defender who can alert on it. The gap is coverage: auditing not enabled means no events. Purple exercises exist precisely to confirm these sources are collected BEFORE an attacker tests them."},
                        {"type": "practice", "command": "curl -I http://example.com", "instructions": "On a Windows lab: check autostart locations (shell:startup, Run keys, schtasks /query). On this sandbox, note how each OS exposes its equivalent persistence surface."},
                    ],
                    'questions': [
                        _q(1, "easy", "The per-user registry autostart chain ends in which subkey name? (one word)", "run"),
                        _q(2, "medium", "Installing a new service generates which Windows event ID? (number)", "7045"),
                        _q(3, "medium", "The per-user autostart folder, opened via shell:startup — one word?", "startup", "start up", "programs"),
                        _q(4, "medium", "Persistence that fires payload on WMI events or timers — name the mechanism. (one phrase)", "wmi subscription", "event subscription", "wmi", "permanent event subscription"),
                        _q(5, "hard", "Which Sysinternals tool inventories autostart entries across every location at once? (one word)", "autoruns"),
                    ],
                },
                {
                    'order_index': 3,
                    'title': 'Credential Access & Reuse',
                    'blocks': [
                        {"type": "text", "heading": "Where Credentials Live in Memory", "body": "Windows caches logon material in LSASS — the Local Security Authority process — so it can authenticate network resources without re-prompting. Dump it (mimikatz sekurlsa::logonpasswords, or a comsvcs.dll mini-dump), and plaintext or replayable material falls out for every recent session. Defense (LSASS protection, credential guard) and offense have circled this process for a decade."},
                        {"type": "text", "heading": "Kerberos Attacks: Roasting", "body": "Kerberos authenticates Active Directory. Kerberoasting: request service tickets for accounts with service principal names, then crack the tickets OFFLINE against the service account's password hash — no noisy logons, just math. AS-REP roasting targets accounts without pre-authentication. The reliable fix is long, random service-account passwords — length defeats the crack."},
                        {"type": "text", "heading": "Reuse: The Whole Point", "body": "Access is worthless until reused. NTLM pass-the-hash replays captured hashes without cracking; Kerberos tickets ride the same golden-ticket path with krbtgt hashes; reused passwords hop hosts directly. Attackers do not crack what they can replay — which reframes every hash as a live credential until proven rotated."},
                        {"type": "text", "heading": "Defensive Mirrors", "body": "Every technique names its defense: LSA protection and guarded access for LSASS; tiered administration so domain hashes never touch workstations; krbtgt rotation; long service-account passwords killing Kerberoasting; SMB signing neutering relay. Red teams that can explain the mirror write better reports — and purple teams that know both sides patch the real gap."},
                        {"type": "practice", "command": "cat /etc/passwd | head -10", "instructions": "Read the account map on the sandbox — the Linux analogue of enumerating principals before any credential attack. Note service accounts that exist."},
                    ],
                    'questions': [
                        _q(1, "easy", "Which Windows process caches authentication material in memory? (acronym)", "lsass"),
                        _q(2, "medium", "Which tool made sekurlsa::logonpasswords famous? (one word)", "mimikatz"),
                        _q(3, "medium", "Requesting Kerberos service tickets for SPN accounts and cracking them offline — one word?", "kerberoasting", "kerberoast"),
                        _q(4, "hard", "Which file in Active Directory stores every account's password hashes? (filename)", "ntds.dit", "ntds", "ntds.dit file"),
                        _q(5, "medium", "Authenticating with a captured hash WITHOUT reversing it — name the technique. (two words, or PTH)", "pass the hash", "pass-the-hash", "pth"),
                    ],
                },
                {
                    'order_index': 4,
                    'title': 'Lateral Movement',
                    'blocks': [
                        {"type": "text", "heading": "The Hop", "body": "Lateral movement is privilege expansion through the estate: valid credentials applied to the next host. The pattern is repetitive — harvest, test (does this password work HERE?), move — because password reuse makes credentials that work on one box work on dozens. Modern intrusions are less exploit chains than credential walks across predictable trust."},
                        {"type": "text", "heading": "The Techniques", "body": "PsExec-style: connect admin share (445), drop a service binary, start it — the classic. WMI and WinRM remoting: execute remotely without touching shares. RDP: full interactive control, the goal for many operators. SSH key reuse on mixed estates. Each needs a specific port and privilege combination — the matrix attackers keep in their notes."},
                        {"type": "text", "heading": "Spray, Then Walk", "body": "With a password list but no foothold: spray it across many accounts (one attempt each, dodging lockouts), then walk whatever lands — one valid credential often opens a dozen hosts because administration is uniform. The same uniformity defenders rely on (GPO everywhere) becomes the attacker's leverage: crack one pattern, unlock the estate."},
                        {"type": "text", "heading": "What Blue Sees", "body": "The signature sequence: 4624 Logon Type 3 from host to host, a 4688 process creation and 7045 service install on the destination, then lateral repeats. Blast radius matters — dozens of hosts in minutes screams automated movement. Understanding this visibility is both the red team's evasions (Room 4) and the blue team's detection opportunity: alert on the CHAIN, not any single hop."},
                        {"type": "practice", "command": "ss -tln && ip route", "instructions": "Map listening services and reachable networks — every lateral path starts as a route and an open port on the next box."},
                    ],
                    'questions': [
                        _q(1, "easy", "PsExec-style lateral movement requires which file-sharing port? (number)", "445"),
                        _q(2, "medium", "Which Windows logon type records network logons such as SMB and PsExec? (number)", "3"),
                        _q(3, "medium", "Trying one common password against MANY accounts, staying under lockout thresholds — one word?", "spraying", "password spraying", "spray"),
                        _q(4, "easy", "PowerShell remoting traffic rides on which Windows management protocol? (acronym)", "winrm"),
                        _q(5, "medium", "PsExec communicates with its remote service through which IPC mechanism? (one phrase)", "named pipes", "pipe", "pipes", "ipc"),
                    ],
                },
            ],
        },
        # ------------------------------------------------------------------
        {
            'order_index': 4,
            'title': 'Evading the Blue Team',
            'description': 'Detection logic, telemetry gaps, and what the logs actually show.',
            'lessons': [
                {
                    'order_index': 1,
                    'title': 'What Blue Teams Actually See',
                    'blocks': [
                        {"type": "text", "heading": "The Telemetry Stack", "body": "Defenders see through layers: firewall and proxy logs (destinations, ports, bytes), DNS logs (every lookup), flow records (who talked to whom, when — payload-free), EDR (every process, parent-child chains, file hashes, script content on endpoints), and Windows event logs (logons, service changes, policy edits). Evading one layer often walks straight into another."},
                        {"type": "text", "heading": "EDR vs Antivirus", "body": "Antivirus matches file signatures — catch a known sample. EDR records BEHAVIOR: a process tree (outlook → winword → cmd → powershell), network connections, and memory access, then scores the sequence. Unsigned malware is not invisible to EDR; it is simply one signal among dozens. Attackers increasingly skip malware entirely for the reason this course keeps repeating: binaries are the most-watched artifacts."},
                        {"type": "text", "heading": "Encrypted Is Not Hidden", "body": "HTTPS hides content, not metadata: defenders still see the destination, certificate, SNI, timing, sizes, and JA3 fingerprint. They know WHICH site you contacted, how often, and at what rhythm — even blind to the bytes. Planning C2 against an encrypted-traffic analyzer means shaping the envelope, because the envelope is all they need to find you."},
                        {"type": "text", "heading": "The Reconstructable Timeline", "body": "Security 4624 (logon, with type), 4688 (process creation with command line when enabled), 4104 (PowerShell script block), 7045 (service install) plus EDR and netflow assemble into a narrative analysts can read hour by hour. Every offensive step in this course writes its signature somewhere — the defender's craft is collecting the right layers and reading them fast."},
                        {"type": "practice", "command": "ps aux | head -10", "instructions": "Look at the process listing — this is the field EDR reads continuously on every endpoint. Ask: which of these processes, spawned by which parent, would look normal?"},
                    ],
                    'questions': [
                        _q(1, "easy", "The endpoint platform that records behavior and process trees, not just signatures — three-letter acronym?", "edr"),
                        _q(2, "medium", "Which Windows event ID records process creation? (number)", "4688"),
                        _q(3, "medium", "PowerShell script-block logging writes captured script content to which event ID? (number)", "4104"),
                        _q(4, "medium", "Network records describing who talked to whom, without payloads — three-letter acronym?", "netflow", "flow", "nflow"),
                        _q(5, "medium", "Windows event 4624 with Logon Type 3 indicates logons over which medium? (one word)", "network", "smb", "the network"),
                    ],
                },
                {
                    'order_index': 2,
                    'title': 'Living off the Land',
                    'blocks': [
                        {"type": "text", "heading": "No Malware, No Signature", "body": "Living off the land means attacking with binaries the OS already ships — LOLBins on Windows (PowerShell, certutil, rundll32, mshta, regsvr32, wmic), bash and standard utilities on Linux. Nothing unsigned hits disk, no hash to blocklist, and the process is trusted Microsoft code on its face. The technique is why 'block the malware' defenses collapsed and behavior analytics took over."},
                        {"type": "text", "heading": "The Favorite Binaries", "body": "PowerShell executes downloaded code in memory (-EncodedCommand for obfuscation). certutil downloads AND decodes files — a dual-purpose downloader hiding in a crypto utility. rundll32 and regsvr32 execute DLLs through trusted host processes. mshta runs web-technologies as desktop apps. Each is signed, present, and routinely abused — hence LOLBAS project cataloguing every one."},
                        {"type": "text", "heading": "Why It Still Gets Caught", "body": "The binary is legitimate; the CONTEXT is not. Command-line auditing (4688 with args, 4104 script blocks) exposes encoded PowerShell. Parent-child anomalies scream: winword spawning cmd is abnormal in any policy. AMSI scans script content at runtime. LOLBins lower the signature barrier and RAISE the behavioral bar — defenders alert on relationships, not names."},
                        {"type": "text", "heading": "The Red-Team Reframe", "body": "For operators, living off the land is OPSEC by default: no payload to detonate in a sandbox, no hash for the SOC to pivot on, artifacts indistinguishable from administration — because they ARE administration tooling. The counter-move from blue is equally clear: full command-line capture, script-block logging, and baselines of normal parent-child pairs. The contest moved from files to behavior."},
                        {"type": "practice", "command": "curl --version | head -2", "instructions": "Inventory a built-in tool's capabilities — exactly how a red team scopes a LOLBin: what can this trusted binary do (download, encode, execute) on this box?"},
                    ],
                    'questions': [
                        _q(1, "easy", "The technique of attacking with only built-in OS tools — three words, or its acronym LOLBin?", "living off the land", "lolbin", "lotl", "living off the land"),
                        _q(2, "medium", "Which certutil flag downloads a remote file to disk? (two words as typed: -urlcache)", "-urlcache", "urlcache", "-u"),
                        _q(3, "medium", "mshta executes which web-technology file type for attackers? (acronym)", "hta"),
                        _q(4, "medium", "Defenders alert on unusual parent-child process pairs — what is the term for the link between spawning and spawned process? (two words)", "parent child", "parent-child", "parent process", "process lineage"),
                        _q(5, "easy", "True or false: using only built-in tools means EDR will not notice anything. (true/false)", "false"),
                    ],
                },
                {
                    'order_index': 3,
                    'title': 'Log Evasion & Timestomping',
                    'blocks': [
                        {"type": "text", "heading": "Clearing Logs: the Self-Defeating Move", "body": "The classic cover-up: wevtutil cl Security on Windows, > /var/log/syslog on Linux. But log clearing LOGS ITSELF — Windows fires 1102 ('security log cleared') and System event 104 — creating the loudest alert in the room and confirming something worth hiding happened. Against mature stacks, clearing trades forensic detail for an immediate notification."},
                        {"type": "text", "heading": "Timestomping", "body": "Files carry timestamps forensics love: creation, modification, access. Timestomping (Sysinternals' timestomp, Linux touch) rewrites them to blend artifacts into normal activity — a DLL made last Tuesday looks like it shipped with the OS. The goal is slowing the timeline reconstruction that orders an investigation and pins actions to the intrusion window."},
                        {"type": "text", "heading": "Why It Rarely Works", "body": "NTFS records each file TWICE: $STANDARD_INFORMATION (which timestomping edits) and $FILE_NAME (which it usually misses) — any mismatch flags tampering. The USN journal remembers changes anyway, EDR records first-seen-at timestamps at its own layer, and backup/snapshot systems hold originals. Timestomping succeeds mainly against endpoints with NO telemetry — the machines worth compromising are the ones that watch themselves."},
                        {"type": "text", "heading": "The Honest Takeaway", "body": "Log and timestamp manipulation is increasingly a losing game — layered telemetry was built precisely because attackers edit local records. The lasting lesson for both sides: which layer is AUTHORITATIVE? Centralized, append-only log shipping (SIEM, remote syslog) beats endpoint-local files, because the attacker who owns the endpoint cannot rewrite what already left it."},
                        {"type": "practice", "command": "export HISTFILE=/dev/null && history -c && cat ~/.bash_history 2>/dev/null | tail -3", "instructions": "Practice seeing how history suppression works (and that prior history still exists on disk) — the shell-level analogue of local log tampering."},
                    ],
                    'questions': [
                        _q(1, "medium", "Clearing the Windows Security log triggers which event ID? (number)", "1102"),
                        _q(2, "medium", "Which Sysinternals utility rewrites file timestamps? (one word)", "timestomp"),
                        _q(3, "hard", "In NTFS, timestomping edits $STANDARD_INFORMATION but usually misses which sibling attribute? (one attribute name)", "$file_name", "file_name", "filename", "$filename", "$file name"),
                        _q(4, "easy", "Deleting evidence of cleared logs fails because the CLEARING itself is what? (one word)", "logged", "alerted", "recorded", "detected", "logged too"),
                        _q(5, "medium", "Which HIST* variable, pointed at /dev/null, stops bash writing command history? (one word)", "histfile", "histfile=/dev/null", "$histfile", "hist"),
                    ],
                },
                {
                    'order_index': 4,
                    'title': 'Detection Gaps & Purple Feedback',
                    'blocks': [
                        {"type": "text", "heading": "Every Technique Has a Data Source — or a Gap", "body": "ATT&CK pairs each technique with data sources: scheduled task creation needs 4698 collected; credential dumping needs LSASS access telemetry; PowerShell abuse needs 4104 or module logging. Map technique → required source → actually-collected-here, and the gaps fall out as rows of 'no data'. Those rows are the engagement's most valuable findings — attackers walk through them untouched."},
                        {"type": "text", "heading": "Measure What Happened", "body": "MTTD (mean time to detect) and MTTR (mean time to respond) turn the exercise into numbers: did any alert fire, how long did it take, what would have stopped the chain earlier. A 12-day undetected objective versus a 4-hour detection reframes the whole report — from 'these vulnerabilities exist' to 'this is how your defense performed against them.'"},
                        {"type": "text", "heading": "The Purple Debrief", "body": "Red replays each phase while blue watches the dashboards live: this technique — did you see it? this log — was it collected? this alert — would it have fired? Findings convert directly into detection engineering work items and hardening priorities, ranked by which gaps the objective actually depended on. Both teams leave with the same, verified picture."},
                        {"type": "text", "heading": "Writing It Up", "body": "A red-team report differs from a pentest's: an attack narrative with timeline and objective milestones first, then technique-by-technique detection outcomes (seen/missed/when), then prioritized recommendations tied to ATT&CK and the gaps found. Screenshots of the dashboard prove blue's side; red's logs prove the timeline. Vague recommendations ('improve monitoring') are the failure mode — name the data source instead."},
                        {"type": "practice", "command": "curl -I http://example.com", "instructions": "From the blue side: which log just recorded this request (proxy? netflow? DNS?)? Name the source — the gap-analysis habit applied to your own action."},
                    ],
                    'questions': [
                        _q(1, "easy", "Mean Time To Detect — four-letter acronym?", "mttd"),
                        _q(2, "medium", "The exercise phase where red and blue jointly review what fired — one word?", "debrief", "retrospective", "purple", "washup"),
                        _q(3, "medium", "A technique with NO corresponding collected data source is a defender's what? (one word)", "gap", "blind spot", "visibility gap", "hole"),
                        _q(4, "easy", "True or false: a red-team report should state which detections fired and how fast they fired. (true/false)", "true"),
                        _q(5, "medium", "Which Windows utility's tooling (with its config) captures full command lines and script activity for defenders? (one word)", "sysmon", "sysmon64"),
                    ],
                },
            ],
        },
    ],
}
