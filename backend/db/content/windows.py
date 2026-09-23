"""Windows for Cybersecurity — full course content (4 rooms, 16 lessons).

Windows is the enterprise target: most corporate endpoints, nearly every
Active Directory forest, and a large share of real-world breach timelines
run through it. This course teaches Windows from first principles with a
security lens, mirroring the Linux course's arc: foundations, internals,
attack surface, then defense.

Questions are text-type: the NightBreach sandbox is Linux, so nothing here
depends on a Windows prompt — concepts are graded, labs point the learner
at their own Windows VM.

Answer hashes are computed at import time from the plaintext answers below
(via db.content.common._hash_answers), keeping this file auditable.
"""
from db.content.common import _hash_answers


def _q(order_index, difficulty, prompt, *answers):
    return {
        "order_index": order_index,
        "question_type": "text",
        "difficulty": difficulty,
        "prompt": prompt,
        "answer_hash": _hash_answers(list(answers)),
        "setup_script": None,
    }


PATH = {
    'slug': 'windows-fundamentals',
    'title': 'Windows for Cybersecurity',
    'description': 'Master Windows internals, administration, and attack surface from first principles.',
    'icon': '/windows.svg',
    'order_index': 5,
    'rooms': [
        # ------------------------------------------------------------------
        {
            'order_index': 1,
            'title': 'Windows Foundations',
            'description': 'Architecture, the command line, accounts, and the registry.',
            'lessons': [
                {
                    'order_index': 1,
                    'title': 'Inside Windows — Architecture and Editions',
                    'blocks': [
                        {"type": "text", "heading": "Why Windows Matters to You", "body": "Windows runs most of the world's desks, most corporate servers that matter (directory services, file shares, finance apps), and therefore most real intrusion timelines. Learning Windows is not optional for a security practitioner: it is where the users, the data, and the credentials are."},
                        {"type": "text", "heading": "Kernel and User Mode", "body": "Windows separates execution into kernel mode (the NT kernel, ntoskrnl.exe — full hardware access, where drivers live) and user mode (everything else: your applications and services). User code asks the kernel through documented APIs. This split is the foundation of the platform's security model: a compromised user-mode process should not be able to simply reach into the kernel or other processes."},
                        {"type": "text", "heading": "Editions You Will Meet", "body": "Windows 10/11 (Pro, Enterprise) dominate endpoints; Windows Server (2016, 2019, 2022) runs the infrastructure — Domain Controllers, file servers, DHCP and DNS. Server Core is a stripped, no-GUI install. Each edition ships with different defaults: a defender hardens endpoints differently from Domain Controllers, and an attacker treats a workstation as a stepping stone to the servers."},
                        {"type": "text", "heading": "The Security-Relevant Difference", "body": "Unlike Linux, Windows was designed around a central directory (Active Directory), a single binary registry of configuration, and one vendor's update pipeline. Those three design choices — directory, registry, Windows Update — shape both the attacks you will learn (credential theft, registry persistence, unpatched services) and the defenses."},
                    ],
                    'questions': [
                        _q(1, "easy", "Which Windows component runs in kernel mode and manages hardware — ntoskrnl.exe is its binary name? (two words)", "nt kernel", "the nt kernel", "kernel"),
                        _q(2, "easy", "Which Windows Server edition is commonly installed without a GUI to reduce attack surface? (two words)", "server core"),
                        _q(3, "medium", "Most enterprise identity data — every user and computer account — lives in which Windows technology? (two words)", "active directory", "ad"),
                        _q(4, "medium", "Windows stores most system-wide configuration in a central hierarchical database called the what?", "registry", "the registry"),
                    ],
                },
                {
                    'order_index': 2,
                    'title': 'The Command Line — cmd and PowerShell',
                    "blocks": [
                        {"type": "text", "heading": "Two Shells, One Platform", "body": "cmd.exe is the legacy shell: simple, scriptable with batch files, still everywhere. PowerShell is the modern object-oriented shell — cmdlets named Verb-Noun (Get-Process, Stop-Service), a rich pipeline that passes structured objects rather than text, and access to the whole .NET framework. Security tooling on both sides (admin scripts and attacker tooling) has moved to PowerShell, so fluency in it is non-negotiable."},
                        {"type": "text", "heading": "Paths, Drives and Syntax", "body": "Windows paths start from drive letters (C:\\Users, C:\\Windows\\System32) and use backslashes. System32 holds the core binaries — including cmd.exe and PowerShell itself. Environment variables appear as %PATH% in cmd and $env:PATH in PowerShell. The forward slash works in most contexts too, which matters when you bounce between Linux and Windows."},
                        {"type": "text", "heading": "Getting Help", "body": "cmd offers /? on almost any command (net user /?). PowerShell offers Get-Help and Get-Command — Get-Command *service* finds every cmdlet touching services. An operator who can self-serve help learns twice as fast; a pentester who can enumerate a system's own documentation often finds exactly the feature that was misconfigured."},
                        {"type": "practice", "command": "uname -a", "instructions": "You are on a Linux sandbox — Windows practice happens on your own VM. But note how the concepts map: this course teaches you to translate every Linux habit into its Windows equivalent."},
                    ],
                    'questions': [
                        _q(1, "easy", "Which modern Windows shell passes structured objects through its pipeline rather than plain text?", "powershell"),
                        _q(2, "medium", "PowerShell cmdlets follow a strict two-part naming pattern of verb and what? (one word)", "noun"),
                        _q(3, "medium", "In cmd, appending which two characters to almost any command shows its usage help?", "/?", "help flag", "/?"),
                        _q(4, "easy", "Which directory under C:\\Windows holds the core system binaries like cmd.exe? (two words)", "system32", "c:\\windows\\system32"),
                    ],
                },
                {
                    'order_index': 3,
                    'title': 'Users, Groups and UAC',
                    'blocks': [
                        {"type": "text", "heading": "Accounts and Built-in Groups", "body": "Local accounts live on one machine; domain accounts live in Active Directory and follow the user to any joined machine. Every Windows system ships built-in accounts (Administrator, Guest — usually disabled) and groups whose membership grants real power: Administrators, plus lower-tier groups like Backup Operators and Remote Desktop Users. Enumerating who is in which group is one of the first things done on any system — by admins and attackers alike."},
                        {"type": "text", "heading": "net user and Get-LocalUser", "body": "net user lists local accounts, net user <name> shows one in detail (groups, last logon), net localgroup Administrators shows who holds local admin. PowerShell equivalents: Get-LocalUser, Get-LocalGroupMember. In a domain, the same commands work against AD with /domain. These commands are reconnaissance: cheap, native, and quiet."},
                        {"type": "text", "heading": "UAC — The Split Token", "body": "User Account Control is the elevation prompt. Internally an administrator account holds a filtered token (standard rights, used for normal work) and a full token (unlocked only on elevation). This is why being in the Administrators group is not the same as running as admin — a distinction attackers care about deeply, because some exploits only matter if the process holds the full token, and UAC can sometimes be bypassed entirely."},
                        {"type": "text", "heading": "Why This Matters for Security", "body": "Least privilege on Windows means: users run as standard accounts, admin actions happen deliberately, and service accounts are segregated. Every user with local admin is a persistence and privilege-escalation shortcut for malware. Mapping local admins across a fleet is a classic audit finding."},
                    ],
                    'questions': [
                        _q(1, "easy", "Which cmd command lists local user accounts? (two words)", "net user"),
                        _q(2, "medium", "Which built-in group's membership grants full control of a Windows machine? (one word)", "administrators"),
                        _q(3, "medium", "UAC gives an administrator account a filtered token and a full token. What is this mechanism called? (the acronym)", "uac", "user account control"),
                        _q(4, "medium", "True or false: a member of the Administrators group always runs every process with full admin rights.", "false"),
                        _q(5, "hard", "Giving every user local admin rights primarily increases the risk of what class of attack — persistence, phishing, or privilege escalation? (one word)", "privilege escalation"),
                    ],
                },
                {
                    'order_index': 4,
                    'title': 'The Registry — Configuration and Persistence',
                    'blocks': [
                        {"type": "text", "heading": "A Database of Everything", "body": "The Windows Registry is a hierarchical database of configuration for the OS, services, drivers, and applications. The top-level hives you must know: HKEY_LOCAL_MACHINE (HKLM) — machine-wide settings, HKCU — the current user's settings, plus HKEY_USERS, HKEY_CLASSES_ROOT and HKEY_CURRENT_CONFIG. Permissions on registry keys work like file ACLs, and weak ones are a real privilege-escalation vector."},
                        {"type": "text", "heading": "Run Keys — the Classic Persistence", "body": "HKCU\\...\\CurrentVersion\\Run and its HKLM sibling list programs executed at logon. Malware loves them: add a value pointing at your binary and it survives reboots. Defenders love them too: every forensic triage starts with dumping the Run/RunOnce keys and Startup folders. Tools like Autoruns (Sysinternals) enumerate all autorun locations — there are dozens."},
                        {"type": "text", "heading": "Reading and Writing", "body": "reg query walks keys from the command line (reg query HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run), reg add writes values, reg delete removes them. PowerShell: Get-ItemProperty / Set-ItemProperty. In investigations, the registry also yields timeline gold: NTUSER.dat records last-write times, UserAssist tracks executed GUI programs, and USBSTOR remembers every USB storage device ever attached."},
                        {"type": "text", "heading": "The Security Habit", "body": "Configuration creep is an attack surface: weak ACLs on service keys, stored credentials in scripts under HKCU, AlwaysInstallElevated flags — all registry issues. When you inherit a Windows machine, audit what runs at startup and who can change it; the answer is frequently 'anyone', which means everyone."},
                    ],
                    'questions': [
                        _q(1, "easy", "Which top-level registry hive holds machine-wide settings? (the abbreviation)", "hklm", "hkey_local_machine"),
                        _q(2, "medium", "Which registry locations are the classic malware persistence points at logon? (two words, plural)", "run keys", "run key", "autorun keys"),
                        _q(3, "medium", "Which reg subcommand displays a key's values from the command line? (one word)", "query"),
                        _q(4, "hard", "Which Sysinternals tool enumerates every autostart location on a Windows system? (one word)", "autoruns", "autoruns.exe"),
                    ],
                },
            ],
        },
        # ------------------------------------------------------------------
        {
            'order_index': 2,
            'title': 'Administration and Internals',
            'description': 'Services, NTFS, PowerShell at operator depth, and Active Directory.',
            'lessons': [
                {
                    'order_index': 1,
                    'title': 'Services and Processes',
                    'blocks': [
                        {"type": "text", "heading": "Processes", "body": "tasklist prints running processes with PIDs; Get-Process is the PowerShell equivalent with richer objects; taskkill /PID <n> /F and Stop-Process kill them. Two things to always notice: the parent process (a Word document spawning cmd.exe is a classic phishing indicator) and the command line (Get-CimInstance Win32_Process exposes full arguments — where hidden behavior lives)."},
                        {"type": "text", "heading": "Services", "body": "Services are long-running processes managed by the Service Control Manager — web servers, update agents, antivirus. sc query lists them; sc qc <name> shows a service's configuration including its binary path; net start/stop control them; PowerShell: Get-Service, Start-Service. Services matter to security because they run — often as SYSTEM, the machine's most powerful account — at boot, without anyone clicking anything."},
                        {"type": "text", "heading": "svchost — the Legitimate Crowd", "body": "Many Windows services are DLLs hosted inside shared svchost.exe processes. That design is why malware impersonates svchost: a fake svchost running from a wrong path (not System32), or an unexplained instance, is a red flag every defender learns to check and every attacker learns to fake."},
                        {"type": "text", "heading": "Why Attackers Love Services", "body": "A service you can reconfigure is a privilege escalation: point its binary path at your payload and wait for reboot (or restart it, if permissions allow). Service misconfiguration — weak ACLs, unquoted paths — is among the most common Windows privesc findings in real assessments. You will attack it properly in Room 3."},
                    ],
                    'questions': [
                        _q(1, "easy", "Which cmd command lists running processes with their PIDs? (one word)", "tasklist"),
                        _q(2, "medium", "Which sc subcommand displays a service's configuration, including its binary path? (two letters)", "qc"),
                        _q(3, "medium", "Which account, more powerful than Administrator, is commonly used to run Windows services? (one word)", "system", "local system"),
                        _q(4, "hard", "Why does malware so often name itself svchost.exe? Because the real svchost hosts many services, a fake one blends in — attackers abuse this to achieve what? (one word)", "masquerading", "stealth", "blending in", "camouflage"),
                        _q(5, "medium", "Which PowerShell cmdlet lists full process command lines via WMI/CIM? (three words)", "get-ciminstance win32_process"),
                    ],
                },
                {
                    'order_index': 2,
                    'title': 'NTFS Permissions and Integrity Levels',
                    'blocks': [
                        {"type": "text", "heading": "ACLs on Everything", "body": "Every NTFS object carries a discretionary ACL: Access Control Entries that grant or deny principals (users/groups) specific rights — Read, Write, Modify, Full Control, and more granular ones. Inheritance pushes permissions down the tree, which is both a convenience and a way for one bad grant on a parent folder to leak across a share."},
                        {"type": "text", "heading": "icacls — Reading and Fixing", "body": "icacls <path> prints the ACL; icacls <path> /grant and /deny modify it; /reset rebuilds inherited permissions. WindowsExplorer's Security tab shows the same data graphically. Auditing permissions — who can write to Program Files folders, service directories, scheduled-task folders — is a core hardening step and a core privesc technique: writable locations where privileged code executes are gold."},
                        {"type": "text", "heading": "Integrity Levels and Mandatory Control", "body": "Beyond the DACL, Windows tags processes and objects with integrity levels: Low (browser sandbox), Medium (normal user), High (elevated admin), System. Mandatory Integrity Control blocks lower-integrity processes from writing to higher ones regardless of ACLs — the mechanism behind Internet Explorer/Office protected mode. It is a real mitigation, but one that applies to writes, not to everything."},
                        {"type": "text", "heading": "Shares", "body": "Network shares (net share, Get-SmbShare) layer share permissions on top of NTFS — and the effective right is the more restrictive of the two. Mis-shared folders (Everyone: Full Control on a finance drive) are a perennial finding. Enumeration of shares is equally perennial on the offensive side — you will do it in Room 3."},
                    ],
                    'questions': [
                        _q(1, "easy", "What does NTFS attach to every file and folder to control access — a three-letter acronym? (the acronym)", "acl", "dacl"),
                        _q(2, "medium", "Which command-line utility displays and modifies NTFS permissions? (one word)", "icacls"),
                        _q(3, "medium", "Which integrity level does a normally-launched user process receive? (one word)", "medium"),
                        _q(4, "medium", "When share permissions and NTFS permissions conflict, which right takes effect? (the more restrictive one)", "the more restrictive", "most restrictive", "restrictive"),
                        _q(5, "hard", "A world-writable folder where a SYSTEM service executes its binary is primarily what kind of risk? (two words)", "privilege escalation", "privesc"),
                    ],
                },
                {
                    'order_index': 3,
                    'title': 'PowerShell for Operators',
                    'blocks': [
                        {"type": "text", "heading": "Objects, Not Text", "body": "PowerShell's pipeline moves .NET objects: Get-Service | Where-Object Status -eq Running | Select-Object Name,DisplayName filters live objects rather than parsing strings. Learn five cmdlets and you can operate: Get-*, Set-*, Start-/Stop-*, Get-Help, Get-Member (which reveals what an object can do)."},
                        {"type": "text", "heading": "Execution Policy — Not a Security Boundary", "body": "ExecutionPolicy (Restricted, RemoteSigned, Unrestricted, Bypass) controls whether PowerShell runs script files. It is a seatbelt, not a wall: powershell -ExecutionPolicy Bypass -File x.ps1 overrides it per-process with no admin rights, and attackers do exactly that. Microsoft says so explicitly. Real control comes from the logging and language-mode features you will meet in Room 4."},
                        {"type": "text", "heading": "Remoting", "body": "PowerShell Remoting (Enter-PSSession, Invoke-Command) executes commands on remote hosts over WinRM (ports 5985/5986) — the Windows world's SSH. Legitimate admins live in it; so do attackers who stole credentials, because remoting is authenticated, encrypted, and utterly normal-looking. WinRM exposed + weak credentials is a standard entry vector in internal assessments."},
                        {"type": "text", "heading": "The Dual-Use Lesson", "body": "PowerShell is the sharpest dual-use tool on Windows: deploy software or deploy ransomware, inventory hosts or inventory a stolen domain — same cmdlets, same syntax. That is why blue teams monitor it obsessively and why the defensive features in Room 4 exist. Your goal is to read any PowerShell — offensive or defensive — fluently."},
                    ],
                    'questions': [
                        _q(1, "easy", "Which PowerShell cmdlet displays documentation for another cmdlet? (two words)", "get-help"),
                        _q(2, "medium", "Which cmdlet reveals the properties and methods available on a pipeline object? (two words)", "get-member"),
                        _q(3, "medium", "Which per-process flag bypasses PowerShell's execution policy without admin rights?", "-executionpolicy bypass", "executionpolicy bypass", "-ep bypass"),
                        _q(4, "medium", "PowerShell Remoting runs over which service and ports — WinRM on what port numbers? (give the plaintext port for WinRM)", "5985"),
                        _q(5, "hard", "Which PowerShell feature allows running commands on remote hosts, making stolen credentials immediately useful across a network? (two words)", "powershell remoting", "remoting"),
                    ],
                },
                {
                    'order_index': 4,
                    'title': 'Active Directory — the Crown Jewel',
                    'blocks': [
                        {"type": "text", "heading": "Domain vs Workgroup", "body": "A workgroup is a pile of independent machines. A domain is machines joined to a central directory served by Domain Controllers, with one identity per user across the whole estate. Log in anywhere, permissions everywhere, Group Policy applied uniformly. The overwhelming majority of mid-to-large organizations run domains — which makes AD the single most targeted technology in enterprise security."},
                        {"type": "text", "heading": "Objects and the Schema", "body": "AD stores objects: users, groups, computers, printers, and OUs (organizational units) that arrange them. Each object has attributes (sAMAccountName, memberOf, description...) — and descriptions are a pentest inside joke, because admins write passwords into them. Every object read is potential recon: who is Domain Admin? Which groups nest into which? What does 'ServiceAccounts' contain?"},
                        {"type": "text", "heading": "Group Policy", "body": "Group Policy Objects (GPOs) push settings — password policy, scripts, installed software, firewall rules — to machines and users. GPOs are also an attack path: modify a GPO and every machine it touches executes your change (a real lateral-movement technique). Enumerating GPOs is standard both for hardening audits and for attack planning."},
                        {"type": "text", "heading": "Authentication: NTLM and Kerberos", "body": "Domains authenticate with Kerberos (ticket-based, modern) and legacy NTLM (challenge-response). Both have famous attack families — Kerberoasting extracts service-account credentials from Kerberos tickets; NTLM relay catches and replays authentication handshakes. You will learn the credential mechanics in Room 3 and the detection side in Room 4; here the point is architectural: whoever controls the Domain Controller controls everything."},
                    ],
                    'questions': [
                        _q(1, "easy", "What is a central server that hosts the Active Directory database called? (two words)", "domain controller", "dc"),
                        _q(2, "medium", "Which AD mechanism pushes configuration like password policy and scripts to machines? (the acronym)", "gpo", "group policy"),
                        _q(3, "medium", "Which modern ticket-based protocol does domains prefer over legacy NTLM? (one word)", "kerberos"),
                        _q(4, "hard", "Admins sometimes leak credentials by writing them into which user-visible object attribute? (one word)", "description", "the description field"),
                        _q(5, "medium", "In domain terms, a standalone machine outside any domain is part of a what? (one word)", "workgroup"),
                    ],
                },
            ],
        },
        # ------------------------------------------------------------------
        {
            'order_index': 3,
            'title': 'The Attack Surface',
            'description': 'Enumeration, SMB, credential attacks, and privilege escalation.',
            'lessons': [
                {
                    'order_index': 1,
                    'title': 'Enumerating a Windows Host',
                    'blocks': [
                        {"type": "text", "heading": "Start with the Ports", "body": "A Windows box announces its role by its open ports: 135/49152+ RPC endpoint mapper, 139/445 SMB, 3389 RDP, 5985 WinRM, 88 Kerberos (Domain Controllers), 389/636 LDAP. nmap -sV -p- gives the census; knowing the default port map turns a scan into an instant role assessment — 'that is a DC' — before any exploitation."},
                        {"type": "text", "heading": "Null Sessions and Share Enumeration", "body": "Historically, an unauthenticated 'null session' could list shares, users, and more (the enum4linux/net view legacy — much restricted in modern systems but never fully dead, especially on older servers). Even unauthenticated SMB often yields the hostname, domain name, and OS build via the NTLM challenge — enough to plan with."},
                        {"type": "text", "heading": "Authenticated Enumeration", "body": "Any valid domain credential — including any domain user — unlocks a treasure chest by design: list users and groups (net user /domain), enumerate shares (net view \\host), query computers, read descriptions. Attack tools (BloodHound et al.) turn that into a full graph of who can reach what. Defenders must accept that any credential is a recon key and design delegation accordingly — the principle behind 'tiered admin' models."},
                        {"type": "practice", "command": "ss -tln | head -20", "instructions": "On the Windows side you would run netstat -ano or Get-NetTCPConnection. Here, practice the habit: enumerate listening services and ask what each one announces about the machine."},
                    ],
                    'questions': [
                        _q(1, "medium", "Open port 88 on a Windows machine usually identifies it as what server type? (two words)", "domain controller", "dc"),
                        _q(2, "medium", "On which port does SMB speak? (the number)", "445"),
                        _q(3, "medium", "An unauthenticated SMB connection that historically allowed listing shares and users is called a what session? (two words)", "null session", "null"),
                        _q(4, "hard", "Which port does WinRM/PowerShell Remoting use in its plaintext form? (the number)", "5985"),
                        _q(5, "medium", "Which net command lists shares offered by a remote host? (two words)", "net view", "net view \\\\host"),
                    ],
                },
                {
                    'order_index': 2,
                    'title': 'SMB — from Null Sessions to EternalBlue',
                    'blocks': [
                        {"type": "text", "heading": "The Protocol That Runs the Office", "body": "SMB (Server Message Block) is Windows' file- and printer-sharing protocol — plus named pipes used for remote administration. It is everywhere on networks precisely because everything needs it, which makes it the most valuable protocol in internal attacks: file access, share enumeration, and remote execution (via named pipes and psexec-style tooling) all ride on 445."},
                        {"type": "text", "heading": "SMBv1 and EternalBlue", "body": "SMB version 1 is a relic from the 1990s kept for compatibility — until 2017, when the leaked NSA-developed EternalBlue exploit (MS17-010, patched March 2017) turned it into a remote, unauthenticated code execution against every unpatched Windows host. WannaCry and NotPetya used it to paralyze hospitals, shipping, and governments within days, spreading machine-to-machine with no user interaction at all."},
                        {"type": "text", "heading": "The Real Lessons", "body": "Three, and none of them is 'hack SMB': (1) patching discipline is existential — the worm ate what patches would have prevented; (2) legacy protocols need active retirement — disable SMBv1 (a Windows feature you can turn off), don't leave it 'just in case'; (3) segmentation limits blast radius — networks where workstations can reach every other workstation's 445 gave WannaCry its speed."},
                        {"type": "text", "heading": "Modern SMB Attack Surface", "body": "Post-EternalBlue, SMB attacks shifted: NTLM relay (capturing authentication and replaying it at another host), coercing authenticated machines to connect to the attacker (PetitPotam-style printer/DFSCoerce tricks), and share-sitting — waiting on a writable share for an admin to walk a malicious file into an elevated context. The protocol is patched; the trust patterns around it remain the target."},
                    ],
                    'questions': [
                        _q(1, "easy", "Which legacy SMB version, disabled by default in modern Windows, enabled the EternalBlue attack? (the version)", "smbv1", "smb 1", "smb version 1"),
                        _q(2, "medium", "Which 2017 worm used EternalBlue to spread machine-to-machine, paralyzing organizations worldwide? (the name)", "wannacry", "wannacry ransomware"),
                        _q(3, "medium", "The MS17-010 patch should have prevented WannaCry. What core defensive practice does this underline? (one word)", "patching", "patch management"),
                        _q(4, "hard", "Which SMB attack class captures a host's authentication handshake and replays it against a third machine? (two words)", "ntlm relay"),
                        _q(5, "medium", "Besides file sharing, what SMB feature enables remote command execution tools like psexec? (two words)", "named pipes"),
                    ],
                },
                {
                    'order_index': 3,
                    'title': 'Credentials — SAM, NTLM and LSASS',
                    'blocks': [
                        {"type": "text", "heading": "Where Passwords Live", "body": "Local account password hashes sit in the SAM database (C:\\Windows\\System32\\config\\SAM, locked while running); domain hashes live in the NTDS.dit database on Domain Controllers. Hashes are stored in NTLM format (MD4-based, unsalted). No salt means identical passwords produce identical hashes — which is exactly why rainbow tables and pass-the-hash exist."},
                        {"type": "text", "heading": "LSASS — the Credential Cache", "body": "The Local Security Authority Subsystem Service (lsass.exe) handles authentication and holds credentials in memory — including plaintext for some logon types and reusable hashes/tickets for others. Dumping LSASS memory (mimikatz made it famous; many tools since) is the standard post-exploitation step, and Microsoft's response — Credential Guard virtualizing LSASS — tells you how serious the problem is."},
                        {"type": "text", "heading": "Pass-the-Hash", "body": "Because NTLM authentication accepts the hash as the secret, an attacker who steals a hash can authenticate without ever knowing the password — pass-the-hash. That single property turned 'one compromised workstation' into 'the domain' for a decade of intrusions. Mitigations: Credential Guard, limiting local admin reuse (LAPS — unique local admin passwords per machine), and moving to Kerberos-only authentication where possible."},
                        {"type": "text", "heading": "Kerberoasting — the Domain Twist", "body": "Any domain user can request a Kerberos service ticket for any service account; the ticket is encrypted with the service account's password-derived key. Crack it offline and you own that service account — frequently one with domain-swinging privileges. Defense: long random passwords on service accounts and Group Managed Service Accounts (gMSA), which rotate automatically and cannot be cracked this way."},
                    ],
                    'questions': [
                        _q(1, "medium", "Which file stores local account password hashes? (the three-letter name)", "sam", "the sam", "sam database"),
                        _q(2, "hard", "NTLM hashes are unsalted, enabling precomputed hash attacks. What is the term for those lookup tables? (two words)", "rainbow table", "rainbow tables"),
                        _q(3, "medium", "Authenticating with a stolen NTLM hash instead of a password is called pass-the-what? (one word)", "hash"),
                        _q(4, "medium", "Which process, lsass.exe, caches credentials in memory and is the standard dumping target? (the acronym)", "lsass", "local security authority subsystem service"),
                        _q(5, "hard", "Requesting Kerberos service tickets and cracking them offline to recover service-account passwords is called what? (one word)", "kerberoasting"),
                        _q(6, "medium", "Microsoft's virtualization-based protection that shields LSASS from memory access is called what? (two words)", "credential guard"),
                    ],
                },
                {
                    'order_index': 4,
                    'title': 'Privilege Escalation on Windows',
                    'blocks': [
                        {"type": "text", "heading": "The Goal and the Method", "body": "You land as a normal user; you want SYSTEM. Windows privesc is enumeration: misconfigurations are common, documented, and findable with scripts (winPEAS, PowerUp, Seatbelt). The recurring theme: something privileged (a service, a task, an installer) touches a location or object that a normal user can influence."},
                        {"type": "text", "heading": "Unquoted Service Paths", "body": "A service configured as C:\\Program Files\\Vendor\\tool.exe without quotes makes Windows guess: it tries C:\\Program.exe, then C:\\Program Files\\Vendor.exe, then the real path. If C:\\ is writable by you, drop Program.exe and the service runs it as SYSTEM at next start. The bug is a parsing quirk; the root cause is a world-writable root directory."},
                        {"type": "text", "heading": "Weak Service Permissions", "body": "If your account can reconfigure a service (change its binPath) — common when service ACLs are sloppy — you replace its binary path with your payload and restart it. sc qc shows the config; accesschk (Sysinternals) answers 'which services can I reconfigure?' in seconds. Same story for scheduled tasks with writable binaries, DLL hijacking (privileged app loads a DLL from a path you can write), and AlwaysInstallElevated (an MSI-installer policy that lets a user install as SYSTEM)."},
                        {"type": "text", "heading": "Defender's Checklist", "body": "Every item above is a one-line audit: service paths quoted, service/task/DLL directories writable only by Administrators, AlwaysInstallElevated off, and admins never browse with elevated shells through user-writable folders. Privesc findings are almost always configuration findings — which means they are almost always fixable."},
                    ],
                    'questions': [
                        _q(1, "hard", "In an unquoted service path C:\\Program Files\\Vendor\\tool.exe, Windows tries to execute C:\\Program.exe first. What must the attacker control to exploit this? (one word)", "c:\\", "the root directory", "c drive root"),
                        _q(2, "medium", "Reconfiguring a weakly-permitted service's binary path to execute your payload is what class of attack? (two words)", "privilege escalation", "privesc"),
                        _q(3, "hard", "Which MSI-installer registry policy, when enabled, lets any user install packages as SYSTEM? (three words)", "alwaysinstallelevated", "always install elevated"),
                        _q(4, "medium", "Placing a malicious DLL in a directory a privileged application searches first is called DLL what? (one word)", "hijacking", "hijack"),
                        _q(5, "medium", "Which Sysinternals tool answers 'which services can my account reconfigure?' (two words)", "accesschk", "accesschk.exe"),
                    ],
                },
            ],
        },
        # ------------------------------------------------------------------
        {
            'order_index': 4,
            'title': 'Defense and Mastery',
            'description': 'Logs, hardening, PowerShell monitoring, and the full assessment arc.',
            'lessons': [
                {
                    'order_index': 1,
                    'title': 'Event Logs and Detection',
                    "blocks": [
                        {"type": "text", "heading": "The Event Log System", "body": "Windows records nearly everything: Security (logons, permission changes), System (services, drivers), Application, PowerShell/Operational, Sysmon (when installed). Event Viewer is the GUI; wevtutil qe Security /c:5 /f:text and Get-WinEvent are the CLI. For a defender these logs are the ground truth; for an attacker they are the footprint to understand and minimize."},
                        {"type": "text", "heading": "The Event IDs Worth Memorizing", "body": "4624 successful logon (note Logon Type: 2 console, 3 network, 10 RDP), 4625 failed logon (brute-force signature), 4720 user account created, 4732 added to a group, 7045 new service installed (a classic persistence/psexec indicator), 4688 process creation (if enabled). A handful of IDs covers the majority of intrusion-relevant activity — know them like you know Linux's auth.log."},
                        {"type": "text", "heading": "Sysmon — the Upgrade", "body": "Sysmon (Sysinternals) adds what Windows omits by default: process creation with full command lines and hashes, network connections per process, image loads, raw disk access, clipboard changes — all under configurable rules. With a good config (e.g. SwiftOnSecurity's), Sysmon turns the event log from a summary into a sensor grid, feeding SIEMs for real detection engineering."},
                        {"type": "text", "heading": "Thinking Like a Detector", "body": "Detection is the inverse of the attacks you learned: LSASS access — alert; new service on a workstation — alert; process spawning cmd from Office — alert. Build the habit now: for every technique in this course, ask 'what would this look like in the logs?' That question, asked systematically, is what detection engineers do."},
                    ],
                    'questions': [
                        _q(1, "medium", "Which event ID signals a failed logon attempt? (the number)", "4625"),
                        _q(2, "medium", "Which event ID fires when a new service is installed — a classic persistence indicator? (the number)", "7045"),
                        _q(3, "hard", "A logon with Logon Type 10 in event 4624 means the user connected how? (the acronym)", "rdp", "remote desktop"),
                        _q(4, "medium", "Which Sysinternals tool extends Windows logging with process command lines, hashes, and network connections? (one word)", "sysmon"),
                        _q(5, "easy", "Which built-in GUI displays Windows event logs? (two words)", "event viewer"),
                    ],
                },
                {
                    'order_index': 2,
                    'title': 'Hardening the Windows Host',
                    'blocks': [
                        {"type": "text", "heading": "Attack Surface Reduction", "body": "Strip what is not needed: disable SMBv1, close RDP to the Internet (or put it behind a VPN with MFA), uninstall legacy runtimes, use Server Core where a GUI adds nothing. Windows Defender Application Control and AppLocker let only approved binaries run — the single most disruptive control for commodity malware, which thrives on 'any EXE runs anywhere'."},
                        {"type": "text", "heading": "Credential Protection", "body": "LAPS gives every machine a unique, rotating local Administrator password — killing pass-the-hash across workstations. Credential Guard virtualizes LSASS. Protected Users group disables the most abusable NTLM flows for privileged accounts. Each control attacks one chapter of this course: reuse, dumping, relay."},
                        {"type": "text", "heading": "Patching and BitLocker", "body": "WSUS/Intune/SCCM push updates — and the WannaCry lesson stands: patching is not optional hygiene, it is the wall. BitLocker encrypts volumes, protecting data at rest from offline attacks (stolen laptops, boot-from-USB hash dumping) — with the caveat that pre-boot compromises and TPM-sufficiency debates matter, so pair it with Secure Boot."},
                        {"type": "text", "heading": "Baseline and Verify", "body": "Hardening is a process, not a checkbox: baseline with tools (Microsoft Security Compliance Toolkit, CIS Benchmarks), verify drift continuously, and re-audit after changes. Every hardening item in this lesson maps to a specific attack from Rooms 3 — that mapping is how you justify controls to management."},
                    ],
                    'questions': [
                        _q(1, "medium", "Which Microsoft tool assigns each machine a unique, regularly rotated local admin password? (the acronym)", "laps", "local administrator password solution"),
                        _q(2, "medium", "Which two application whitelisting technologies control what binaries may execute? (the built-in Windows one and the enterprise policy one — give the newer, WDAC)", "wdac", "windows defender application control"),
                        _q(3, "medium", "Which full-disk encryption technology protects Windows data at rest? (one word)", "bitlocker"),
                        _q(4, "easy", "Which legacy protocol should be explicitly disabled to remove the EternalBlue-class risk? (the version)", "smbv1", "smb 1"),
                        _q(5, "hard", "Which CIS/Microsoft artifacts provide hardening baselines you can audit against? (the company behind the Security Compliance Toolkit)", "microsoft"),
                    ],
                },
                {
                    'order_index': 3,
                    'title': 'PowerShell Under the Microscope',
                    'blocks': [
                        {"type": "text", "heading": "Why Monitor PowerShell", "body": "Because attackers live there: PowerShell can download payloads, dump credentials, move laterally, and encrypt itself into obscurity — all without dropping a binary. (Obfuscation families like Invoke-Obfuscation made static scanning useless, which forced the logging improvements below.)"},
                        {"type": "text", "heading": "Script Block Logging (4104)", "body": "Module and script block logging record not just which cmdlets ran but the deobfuscated code that executed — event 4104 captures script blocks as they run. Configuration is Group Policy (Administrative Templates → PowerShell). This is the single highest-value PowerShell telemetry: even heavily obfuscated payloads get logged in clear once the engine parses them."},
                        {"type": "text", "heading": "Constrained Language Mode", "body": "In ConstrainedLanguageMode PowerShell restricts itself to core cmdlets and blocks .NET access, COM, and most add-ons — turning the attacker's favorite shell into a toy. Defenders toggle it for users (via AppLocker policy integration); attackers detect it ($ExecutionContext.SessionState.LanguageMode) and fight to escape. Understand both sides: it is a speed bump with real value, not an absolute wall."},
                        {"type": "text", "heading": "AMSI — the Content Scanner", "body": "The Antimalware Scan Interface passes script content (PowerShell, JScript, VBA macros) to the installed antivirus before execution. Defensive win: obfuscated malicious scripts get caught at runtime regardless of file format. Offensive reality: AMSI bypasses are a constant cat-and-mouse (patching the in-memory DLL, tampering flags). The lesson for defenders: EDR that integrates AMSI matters; the lesson for attackers-in-training: know it exists because every mature environment has it."},
                    ],
                    'questions': [
                        _q(1, "medium", "Which PowerShell event ID captures deobfuscated script blocks as they execute? (the number)", "4104"),
                        _q(2, "medium", "Which PowerShell mode restricts .NET access and add-ons for untrusted users? (three words)", "constrained language mode", "constrainedlanguage"),
                        _q(3, "easy", "Which Windows interface sends script content to antivirus before execution? (the acronym)", "amsi", "antimalware scan interface"),
                        _q(4, "hard", "Script block logging defeats which attacker technique that made static analysis useless? (one word)", "obfuscation"),
                        _q(5, "medium", "True or false: execution policy alone is an effective defense against malicious PowerShell.", "false"),
                    ],
                },
                {
                    'order_index': 4,
                    'title': 'Capstone — the Life of an Assessment',
                    'blocks': [
                        {"type": "text", "heading": "The Arc You Can Now Read", "body": "Recon: nmap the range, read the port map — 445, 3389, 5985; the 88 on one host marks a DC. Enumeration: null-session leftovers, then one phished credential turns into net user /domain and a share list. Credential access: LSASS dump on a workstation, pass-the-hash sideways, Kerberoast a service account. Escalation: unquoted path or weak service ACL to SYSTEM. Persistence: a Run key, a new service (event 7045!). Lateral movement: psexec-style pipes and PowerShell Remoting. You have met every step."},
                        {"type": "text", "heading": "The Same Story in the Logs", "body": "Now flip the tape: 4625 bursts then a 4624 (brute force succeeded), 4624 type 3 from an odd source (remoting), 4688 with whoami and 4104 with obfuscated script blocks, 7045 service install, 4732 group modification, then mass 4624s — the worm moment. Every offensive technique in this course writes its signature; the defender's craft is collecting and reading them in time."},
                        {"type": "text", "heading": "Principles That Survive Version Changes", "body": "Tools change (mimikatz today, whatever tomorrow); principles persist: identity is the perimeter — protect credentials like keys; least privilege everywhere — most of Room 3's attacks need a misconfiguration; assume breach and instrument accordingly — Room 4's logging is how you see; and patch — WannaCry is the permanent exam question. If you internalize those four, new CVEs become routine, not existential."},
                        {"type": "text", "heading": "Where to Go Next", "body": "With Linux, Networking, and Windows foundations you are ready for the specializations: Web App Pentesting (attacks the applications on top of these platforms), Defensive Security (the blue-team depth of Room 4), and Offensive Security (the full kill chain, hands on). This course's questions asked you to think in both directions — that duality is the profession."},
                    ],
                    'questions': [
                        _q(1, "medium", "In the assessment arc, which event ID reveals the attacker's persistence-by-service moment? (the number)", "7045"),
                        _q(2, "hard", "Which single principle, 'identity is the what', summarizes where the modern perimeter moved to? (one word)", "perimeter"),
                        _q(3, "medium", "A flood of 4625 followed by one 4624 is the log signature of which attack? (two words)", "brute force", "password brute force"),
                        _q(4, "medium", "Which principle states users and services get the minimum rights needed — denying Room 3's privesc its misconfigurations? (two words)", "least privilege"),
                        _q(5, "hard", "Enumerate, escalate, persist, move laterally — collecting these into one term: what does the 'kill' in 'kill chain' describe? Answer with the two-word term for the full attacker path.", "kill chain", "attack chain"),
                    ],
                },
            ],
        },
    ],
}
