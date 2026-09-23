"""Paths awaiting full content.

- defensive-security: placeholder from the original roadmap.
- web-pentesting / network-pentesting / red-teaming: the three divisions of
  the former offensive-security path. Room skeletons below define the
  curriculum; lessons and questions are implemented per room in follow-ups.
"""

PATHS = [
    {
        'slug': 'defensive-security',
        'title': 'Defensive Security',
        'description': 'Learn to detect, prevent, and mitigate attacks and harden systems.',
        'icon': '/defensive.jpeg',
        'order_index': 4,
        'rooms': [],
    },
    {
        'slug': 'web-pentesting',
        'title': 'Web App Pentesting',
        'description': 'Recon, exploit, and harden web applications — from HTTP fundamentals to authentication attacks.',
        'icon': '/webapppentest.jpg',
        'order_index': 6,
        'rooms': [
            {
                'order_index': 1,
                'title': 'Web Fundamentals for Attackers',
                'description': 'HTTP mechanics, headers, cookies, and how servers really talk.',
                'lessons': [],
            },
            {
                'order_index': 2,
                'title': 'Recon & Mapping',
                'description': 'Directory discovery, technology fingerprinting, and attack-surface mapping.',
                'lessons': [],
            },
            {
                'order_index': 3,
                'title': 'Injection Attacks',
                'description': 'SQL injection, command injection, and template injection.',
                'lessons': [],
            },
            {
                'order_index': 4,
                'title': 'Authentication & Session Attacks',
                'description': 'Brute force, session handling flaws, and access control failures.',
                'lessons': [],
            },
        ],
    },
    {
        'slug': 'network-pentesting',
        'title': 'Network Pentesting',
        'description': 'Scan, enumerate, and exploit network services and hosts — nmap to exploitation.',
        'icon': '/Networking.jpg',
        'order_index': 7,
        'rooms': [
            {
                'order_index': 1,
                'title': 'Scanning & Enumeration',
                'description': 'Host discovery, port scanning, service and OS fingerprinting at operator depth.',
                'lessons': [],
            },
            {
                'order_index': 2,
                'title': 'SMB & Windows Services',
                'description': 'Enumerating and exploiting SMB, RPC, and Windows network services.',
                'lessons': [],
            },
            {
                'order_index': 3,
                'title': 'Linux Services & Exploitation',
                'description': 'Enumerating SSH, FTP, and web services; finding and using public exploits.',
                'lessons': [],
            },
            {
                'order_index': 4,
                'title': 'Post-Exploitation & Pivoting',
                'description': 'Shells, privilege escalation basics, and moving through networks.',
                'lessons': [],
            },
        ],
    },
    {
        'slug': 'red-teaming',
        'title': 'Red Teaming',
        'description': 'Adversary simulation: C2, persistence, lateral movement, and evading detection.',
        'icon': '/redteam.svg',
        'order_index': 8,
        'rooms': [
            {
              'order_index': 1,
                'title': 'Red Team Methodology',
                'description': 'Objectives, threat emulation, rules of engagement, and OPSEC.',
                'lessons': [],
            },
            {
                'order_index': 2,
                'title': 'Command & Control',
                'description': 'C2 infrastructure, channels, and beaconing.',
                'lessons': [],
            },
            {
                'order_index': 3,
                'title': 'Persistence & Lateral Movement',
                'description': 'Staying in, moving sideways, and credential reuse across the estate.',
                'lessons': [],
            },
            {
                'order_index': 4,
                'title': 'Evading the Blue Team',
                'description': 'Detection logic, telemetry gaps, and what the logs actually show.',
                'lessons': [],
            },
        ],
    },
]
