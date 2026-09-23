"""Placeholder paths that exist in the roadmap but have no content yet."""

PATHS = [    {
    'slug': 'fundamental-cybersecurity',
    'title': 'Cyber Security',
    'description': 'Core principles of information security, risk management, and threat landscapes.',
    'icon': '/fundamentalCybersecurity.jpeg',
    'order_index': 3,
    'rooms': [
    ],
},
    {
    'slug': 'defensive-security',
    'title': 'Defensive Security',
    'description': 'Learn to detect, prevent, and mitigate attacks and harden systems.',
    'icon': '/defensive.jpeg',
    'order_index': 4,
    'rooms': [
    ],
},
    {
    'slug': 'offensive-security',
    'title': 'Offensive Security',
    'description': 'Understand ethical hacking techniques, vulnerability exploitation, and post-exploitation.',
    'icon': '/offensive.jpeg',
    'order_index': 5,
    'rooms': [
{
    'order_index': 1,
    'title': 'Cybersecurity Zero',
    'description': 'Core principles, threat landscapes, and mindset.',
    'lessons': [],
},
{
    'order_index': 2,
    'title': 'Linux Command Line',
    'description': 'Mastering the essential hacking OS.',
    'lessons': [],
},
{
    'order_index': 3,
    'title': 'Networking Essentials',
    'description': 'Protocols, subnetting, and traffic analysis for offense.',
    'lessons': [],
},
{
    'order_index': 4,
    'title': 'Recon & OSINT',
    'description': 'Passive information gathering techniques.',
    'lessons': [
        {
            'order_index': 1,
            'title': 'Scanning with Nmap',
            'blocks': [
                {"type": "text", "heading": "What is Nmap?", "body": "Nmap (Network Mapper) is the standard tool for discovering what's running on a network. Given a target, it tells you which ports are open, what service is listening on each one, and often the exact software version — the first step in almost any real penetration test."},
                {"type": "text", "heading": "Why Scan First?", "body": "You can't attack what you don't know exists. Before trying any exploit, a pentester needs to know: is the target alive? Which ports respond? What service is behind each port? Nmap answers all three questions in one command."},
                {"type": "text", "heading": "A Basic Scan", "body": "The simplest form is `nmap <target>` — for example `nmap localhost` or `nmap 192.168.1.10`. This checks the 1,000 most common ports and reports which are open, closed, or filtered."},
                {"type": "text", "heading": "Service Detection", "body": "Adding `-sV` tells Nmap to probe each open port further and guess the exact service and version running there, e.g. 'OpenSSH 8.9' instead of just 'port 22 open'. This is often the detail that tells you which known vulnerability to try."},
                {"type": "practice", "command": "nmap -sV localhost", "instructions": "Run nmap -sV localhost in the terminal and note what services it reports."}
            ],
            'questions': [
                {
                    'order_index': 1,
                    'question_type': 'text',
                    'difficulty': 'easy',
                    'prompt': 'What flag tells Nmap to detect the version of services running on open ports?',
                    'answer_hash': '1af832b1983fe2d07b0e452da1233b5ef3396582abe43116e3ac3085360fec01',
                    'setup_script': None,
                },
                {
                    'order_index': 2,
                    'question_type': 'terminal',
                    'difficulty': 'easy',
                    'prompt': 'Run nmap -sV localhost in your terminal. Which port number does it report as open?',
                    'answer_hash': '785f3ec7eb32f30b90cd0fcf3657d388b5ff4297f2f9716ff66e9b69c05ddd09',
                    'setup_script': None,
                },
            ],
        },
    ],
},
{
    'order_index': 5,
    'title': 'Vulnerability Research',
    'description': 'Finding and analyzing weaknesses.',
    'lessons': [],
},
{
    'order_index': 6,
    'title': 'Exploitation Frameworks',
    'description': 'Using tools to gain access.',
    'lessons': [],
},
{
    'order_index': 7,
    'title': 'Web App Pentesting',
    'description': 'OWASP Top 10 and advanced web attacks.',
    'lessons': [],
},
{
    'order_index': 8,
    'title': 'Privilege Escalation',
    'description': 'Moving from user to admin, staying hidden.',
    'lessons': [],
},
{
    'order_index': 9,
    'title': 'Advanced Red Teaming',
    'description': 'Full-scope adversarial simulations.',
    'lessons': [],
},
],
}
]
