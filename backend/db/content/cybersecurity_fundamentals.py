"""Cybersecurity Fundamentals — full course content (4 rooms, 16 lessons).

The zero-knowledge starting point: what security is, how systems decide who
you are, how cryptography protects data, why humans are the weakest link,
what the threat landscape looks like, the vocabulary of risk, and the ethics
and careers of the profession. Every chapter keeps a dual lens — how each
idea is attacked and how it is defended.

Questions are text-type (the sandbox is Linux; nothing here needs a shell).
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
    'slug': 'fundamental-cybersecurity',
    'title': 'Cyber Security',
    'description': 'Core principles of information security, risk management, and threat landscapes.',
    'icon': '/fundamentalCybersecurity.jpeg',
    'order_index': 3,
    'rooms': [
        # ------------------------------------------------------------------
        {
            'order_index': 1,
            'title': 'Foundations & the CIA Triad',
            'description': 'What security protects, and the model behind every security decision.',
            'lessons': [
                {
                    'order_index': 1,
                    'title': 'What Is Cybersecurity?',
                    'blocks': [
                        {"type": "text", "heading": "The Job Description", "body": "Cybersecurity is the practice of protecting systems, networks, and data from digital attack, damage, or unauthorized access. Strip the buzzwords and it is the management of risk: perfect security does not exist, so professionals decide which risks to reduce, which to accept, and which to transfer — and prove those decisions with controls."},
                        {"type": "text", "heading": "Assets, Threats, Attackers", "body": "Three nouns anchor everything. An asset is anything valuable: customer data, uptime, reputation, a credential. A threat is anything that could harm an asset — from ransomware to a flooded data center. The actors behind threats span curious script kiddies, organized crime chasing money, hacktivists chasing messages, and nation-states chasing leverage. Security exists because somebody, somewhere, wants what you have."},
                        {"type": "text", "heading": "Why This Field Exists", "body": "Every business process that went digital inherited the crimes of the physical world — theft, fraud, extortion, espionage — plus new ones only software makes possible. The 2017 WannaCry outbreak shut hospitals; billions of records have leaked from single misconfigured buckets. Security is not an IT checkbox; it is the discipline that lets an organization keep its promises."},
                        {"type": "text", "heading": "The Course Ahead", "body": "This room builds your model of what security protects. The rest of the course teaches how it fails and how it is defended: identity (Room 2), cryptography (Room 2), people (Room 3), malware and attackers (Room 3), risk and principles (Room 4). Keep a running example in your head — a small online shop — and test every concept against it."},
                    ],
                    'questions': [
                        _q(1, "easy", "An item of value that needs protection — data, uptime, reputation — is called an what?", "asset"),
                        _q(2, "easy", "Anything that could potentially harm an asset is called a what? (one word)", "threat"),
                        _q(3, "medium", "Which attacker class is primarily motivated by financial gain? (two words)", "organized crime", "cybercrime", "cybercriminals"),
                        _q(4, "medium", "True or false: perfect, absolute security is achievable with enough budget.", "false"),
                        _q(5, "medium", "Security is best described as the ongoing management of what? (one word)", "risk"),
                    ],
                },
                {
                    'order_index': 2,
                    'title': 'The CIA Triad',
                    'blocks': [
                        {"type": "text", "heading": "Three Letters Behind Every Decision", "body": "Confidentiality — only authorized eyes see the data (encryption, access controls). Integrity — data is accurate and untampered (hashing, signatures, checksums). Availability — systems are usable when needed (redundancy, backups, DDoS protection). Every control you will ever deploy, and every attack you will ever study, maps to at least one of these."},
                        {"type": "text", "heading": "Confidentiality in Practice", "body": "A leaked database of passwords is a confidentiality failure; so is an intern reading HR files they can access but shouldn't. Controls: encryption at rest and in transit, least-privilege access, data classification. Attacks: breaches, eavesdropping, insider snooping."},
                        {"type": "text", "heading": "Integrity and Availability in Practice", "body": "Integrity fails when a defaced website shows the attacker's message, or a silently modified invoice routes payment to the wrong account. Controls: hashing, digital signatures, version control, audit logs. Availability fails under ransomware that encrypts everything, a DDoS that drowns a storefront, or a forklift through the server closet. Controls: redundancy, backups, rate limiting, incident response."},
                        {"type": "text", "heading": "Classifying Incidents", "body": "Practice the mapping — it is the skill: ransomware encrypts your database (availability), a breach of customer emails (confidentiality), a man-in-the-middle altering a bank transfer (integrity). Famous cases: WannaCry hammered availability; the Ashley Madison leak destroyed confidentiality; stuxnet famously altered physical outcomes — integrity. One incident can break all three."},
                    ],
                    'questions': [
                        _q(1, "easy", "Which element of the CIA triad means only authorized people can read the data? (one word)", "confidentiality"),
                        _q(2, "easy", "Which element means data stays accurate and untampered? (one word)", "integrity"),
                        _q(3, "easy", "Which element means systems are usable when needed? (one word)", "availability"),
                        _q(4, "medium", "Ransomware that encrypts every file primarily violates which CIA element? (one word)", "availability"),
                        _q(5, "medium", "A website defaced with an attacker's banner primarily violates which element? (one word)", "integrity"),
                        _q(6, "medium", "Name one classic defense of confidentiality that uses mathematics to protect data. (one word)", "encryption", "access control", "cryptography"),
                    ],
                },
                {
                    'order_index': 3,
                    'title': 'The Attacker View — DAD and Beyond',
                    'blocks': [
                        {"type": "text", "heading": "DAD: The Mirror of CIA", "body": "Attackers do the opposite of the triad: Disclosure (expose secrets — breaks confidentiality), Alteration (tamper — breaks integrity), Destruction (deny service — breaks availability). When you analyze any incident, translating attacker actions into DAD verbs and then into CIA failures is the whole assessment."},
                        {"type": "text", "heading": "Parkerian Hexad (Light Touch)", "body": "The CIA triad is a simplification. The Parkerian Hexad adds: Possession (someone holds your encrypted laptop — no data read, but not yours), Authenticity (is this data genuinely from who it claims?), and Utility (data is intact but unusable — encrypted without the key is intact yet useless). You will rarely cite it in practice, but knowing it stops the classic exam trap of 'encrypted laptop stolen = confidentiality breach?'"},
                        {"type": "text", "heading": "Non-repudiation and Accountability", "body": "Non-repudiation means an action cannot credibly be denied later — a signed order, a logged transaction with identity bound in. Accountability means every action traces to an identity (unique accounts, logs, no shared 'admin' passwords). Both matter because breaches are investigated after the fact: you must be able to prove who did what."},
                        {"type": "text", "heading": "The Hospital Scenario", "body": "Classic exam exercise, and a real pattern: attackers encrypt a hospital's records (destruction/availability), threaten to leak patient data (disclosure/confidentiality), and alter one pharmacy order to prove access (alteration/integrity). Three letters, one story — and you can now explain to management exactly what was lost and what that implies for response priorities."},
                    ],
                    'questions': [
                        _q(1, "easy", "In the attacker's mirror of CIA, D stands for what? (one word)", "disclosure"),
                        _q(2, "medium", "An attacker changes a victim's invoice data. Which DAD verb and which CIA element pair correctly? (DAD verb: one word)", "alteration"),
                        _q(3, "medium", "An action bound to an identity so strongly it cannot later be denied is called non-what? (one word)", "repudiation", "non-repudiation"),
                        _q(4, "hard", "A thief steals an encrypted, powered-off laptop. Data cannot be read, yet something is still lost — which Parkerian property? (one word)", "possession"),
                        _q(5, "medium", "Every action traceable to a unique, individual identity is called what? (one word)", "accountability"),
                    ],
                },
                {
                    'order_index': 4,
                    'title': 'Incident Lab — Classifying Real Breaches',
                    'blocks': [
                        {"type": "text", "heading": "The Method", "body": "Take any incident and answer in order: What was the attacker's action in DAD terms? Which CIA element(s) broke? Which controls would have reduced or detected it? This is the muscle you will train for the rest of your career — in post-incident reviews, risk registers, and board reports alike."},
                        {"type": "text", "heading": "Five Quick Cases", "body": "(1) Equifax 2017: unpatched web framework, 147M identities disclosed — confidentiality. (2) WannaCry 2017: worm encrypts hospitals — availability. (3) A defacement during a hacktivist campaign — integrity. (4) Colonial Pipeline 2021: one stolen VPN password → fuel panic — availability plus confidentiality of credentials. (5) A DDoS on an election-info site — availability, purely."},
                        {"type": "text", "heading": "Defenses per Element", "body": "Build your first control matrix. Confidentiality: encryption, least privilege, classification. Integrity: hashing, signatures, audit logging. Availability: backups, redundancy, DDoS protection, patching. The inverse matrix is equally instructive — three attacks per element: eavesdropping/insider leaks; tampering/forged transfers; DDoS/ransomware/worms."},
                        {"type": "text", "heading": "What This Lab Trains", "body": "Security reports live and die on precise language. 'We got hacked' is not a finding; 'an attacker used a stolen credential to alter customer order data, an integrity failure undetected for nine days' is. From here on, every exercise in this course expects you to name the element, the verb, and the control."},
                    ],
                    'questions': [
                        _q(1, "medium", "Equifax (2017): 147M records exposed via an unpatched server. Primary CIA violation? (one word)", "confidentiality"),
                        _q(2, "medium", "Colonial Pipeline (2021): operations halted after one compromised VPN login. Primary CIA violation? (one word)", "availability"),
                        _q(3, "medium", "Which DAD verb pairs with a DDoS attack? (one word)", "destruction"),
                        _q(4, "hard", "Name the single control class that most directly protects integrity of files at rest. (one word)", "hashing", "signatures", "checksums"),
                        _q(5, "medium", "A backup that restores operations after ransomware primarily protects which element? (one word)", "availability"),
                    ],
                },
            ],
        },
        # ------------------------------------------------------------------
        {
            'order_index': 2,
            'title': 'Identity & Cryptography',
            'description': 'How systems decide who you are and what you may do — and how math protects data.',
            'lessons': [
                {
                    'order_index': 1,
                    'title': 'AAA and the Authentication Factors',
                    'blocks': [
                        {"type": "text", "heading": "Identification, Authentication, Authorization", "body": "Three steps people blur constantly. Identification: you claim an identity (a username). Authentication: you prove it (a password, a token, a fingerprint). Authorization: the system decides what that identity may do. A useful mantra: 'who are you, prove it, and what are you allowed to touch?' Accounting — logging what you did — completes the AAA framework (RADIUS/TACACS+ made it standard in network gear)."},
                        {"type": "text", "heading": "The Three Factors", "body": "Something you know (passwords, PINs), something you have (phone app, smart card, hardware key), something you are (fingerprint, face). Two factors of the same type — two passwords, password plus PIN — are not MFA, they are multi-knowledge. Real MFA mixes factor types, which is why a stolen password alone stops working."},
                        {"type": "text", "heading": "MFA vs 2FA vs 2SV", "body": "2FA = two different factor types. 2SV (two-step verification) = password plus an OTP sent over the same knowledge channel — still better than a password alone, but weaker than true MFA. And not all MFA is equal: SMS codes are phishable and SIM-swappable; app-based TOTP is stronger; hardware keys (FIDO2) are phishing-resistant because the protocol cryptographically binds the login to the legitimate site."},
                        {"type": "text", "heading": "Where This Shows Up in Attacks", "body": "Every major account-takeover campaign begins with the gap between these concepts: credential stuffing attacks reuse leaked passwords; MFA fatigue attacks spam push notifications hoping for an approval; adversary-in-the-middle proxies phish OTPs in real time. Knowing why each works tells you exactly which control defeats it."},
                    ],
                    'questions': [
                        _q(1, "easy", "Proving you are the owner of an identity is called what? (one word)", "authentication"),
                        _q(2, "easy", "Deciding what an authenticated identity may do is called what? (one word)", "authorization"),
                        _q(3, "medium", "A password plus a fingerprint combines which two factor types? (two words, comma-separated)", "knowledge, biometric", "something you know, something you are"),
                        _q(4, "medium", "A password plus a PIN is not MFA because both factors are the same what? (one word)", "type", "category", "knowledge"),
                        _q(5, "hard", "Which MFA method is considered phishing-resistant because it cryptographically binds the login to the real site? (three words)", "fido2 hardware key", "hardware security key", "fido2"),
                        _q(6, "medium", "In AAA, which letter covers logging what the user did? (one word)", "accounting"),
                    ],
                },
                {
                    'order_index': 2,
                    'title': 'Passwords, Storage and Access Models',
                    'blocks': [
                        {"type": "text", "heading": "Password Storage Done Right", "body": "Passwords must never be stored in plain text or fast hashes. A password policy governs length, complexity, rotation and reuse — modern guidance (NIST 800-63) favors long passphrases over short complex strings, blocks breached passwords, and drops forced periodic rotation, which mostly drives Post-it notes. Password managers make unique-per-site passwords realistic; passkeys (FIDO2 credentials bound to a site) are replacing passwords outright."},
                        {"type": "text", "heading": "Hashing with a Salt", "body": "A salt is a random value stored with each password hash, forcing attackers to crack each hash individually instead of reusing rainbow tables. Purpose-built password hashes — bcrypt, scrypt, Argon2 — add tunable slowness (key stretching) so a billion guesses costs a billion CPU-years instead of seconds. When a breach leaks 'unsalted MD5', the fallout tells you exactly why salts and slow hashes exist."},
                        {"type": "text", "heading": "The Access Control Models", "body": "DAC (discretionary): owners set permissions — flexible, defaults to chaos. MAC (mandatory): labels and classifications decide — military style, rigid. RBAC (role-based): permissions attach to roles (teller, admin), users get roles — the enterprise default. ABAC (attribute-based): policies evaluate attributes (department, time, device health) — the modern, fine-grained model. Each is a different answer to 'who may do what, and who decides?'"},
                        {"type": "text", "heading": "The Four Design Principles", "body": "Least privilege: grant the minimum rights needed — nothing more. Need-to-know: even authorized users only see what their task requires. Separation of duties: no single person can both create and approve a payment. Defense in depth: assume any one control fails and stack layers. Every architecture you will ever review is measured against these four."},
                        {"type": "text", "heading": "SSO and Federation", "body": "Single sign-on lets one identity serve many systems (one corporate login for everything). Federation extends it across organizations: your identity provider (Okta, Entra ID) asserts who you are to other services via standards like SAML or OIDC. Huge usability win — and a huge single point of failure, which is why compromising an identity provider is the modern jackpot for attackers."},
                    ],
                    'questions': [
                        _q(1, "easy", "Granting users only the minimum rights they need is called least what? (one word)", "privilege"),
                        _q(2, "medium", "Which password hashing algorithm is purpose-built with a salt and tunable slowness? (give one: bcrypt or argon2)", "bcrypt", "argon2", "scrypt"),
                        _q(3, "medium", "A random value stored with each password hash to defeat rainbow tables is called a what? (one word)", "salt"),
                        _q(4, "medium", "Which access control model attaches permissions to job roles rather than individual users? (the acronym)", "rbac", "role-based access control"),
                        _q(5, "hard", "Which model uses labels and classifications — like 'top secret' — to enforce access? (the acronym)", "mac", "mandatory access control"),
                        _q(6, "medium", "No single person should both create and approve a payment. Which principle is this? (two words)", "separation of duties", "separation"),
                        _q(7, "medium", "One corporate login for many internal systems is called single what? (one word)", "sign-on", "sign on", "sso"),
                    ],
                },
                {
                    'order_index': 3,
                    'title': 'Cryptography — Encryption, Hashing, Encoding',
                    'blocks': [
                        {"type": "text", "heading": "Vocabulary First", "body": "Plaintext: readable data. Ciphertext: scrambled data. Key: the secret parameter. Cipher: the algorithm. Kerckhoffs' principle — the system must remain secure even if everything except the key is public — is why 'nobody can guess our algorithm' is never a security argument."},
                        {"type": "text", "heading": "The Classic Beginner Trap", "body": "Encoding (Base64) is a format change anyone can reverse — it has NO key and NO secrecy. Hashing (MD5, SHA-256) is one-way: no key, no reversal, used to verify integrity. Encryption is reversible but requires a key. Obfuscation just makes things ugly. When a junior dev calls Base64 'encryption', attackers get free access to whatever that assumption protected. Drill: given a blob, ask — can it be reversed (encryption/encoding) or only verified (hashing)? Does reversal need a key (encryption) or not (encoding)?"},
                        {"type": "text", "heading": "Symmetric vs Asymmetric", "body": "Symmetric: one shared key, fast, used for bulk data — AES is today's standard; DES/3DES are retired; modes matter (ECB leaks patterns — never use it). Asymmetric: a keypair (public to encrypt/verify, private to decrypt/sign) — RSA and ECC; slow, used for key exchange and signatures, not bulk data. Diffie-Hellman lets two strangers derive a shared secret over a public channel — the trick that makes encrypted handshakes possible."},
                        {"type": "text", "heading": "Hybrid Encryption — How TLS Actually Works", "body": "Real protocols combine both: asymmetric crypto authenticates and agrees a session key (or via DH), then fast symmetric crypto encrypts the actual traffic. HTTPS on a login page: certificate proves the server's identity, key exchange establishes a session key, symmetric cipher protects your password in flight. When people say 'TLS uses RSA', the precise answer is: for identity and key agreement at the start; everything after is symmetric."},
                        {"type": "text", "heading": "Signatures, Certificates and PKI", "body": "A digital signature = hash of the message, encrypted with the signer's private key — providing integrity, authenticity, non-repudiation in one operation. Certificates bind a public key to an identity, signed by a Certificate Authority; browsers trust a pre-installed set of CAs and build the chain to them — that is the padlock. When a CA is compromised or a certificate is issued wrongly, trust itself becomes the vulnerability."},
                    ],
                    'questions': [
                        _q(1, "easy", "Which is reversible without any key: hashing, encryption, or encoding? (one word)", "encoding", "base64"),
                        _q(2, "easy", "Hashing is a one-what function — you can verify but never recover the input? (one word)", "way", "one-way"),
                        _q(3, "medium", "Which symmetric algorithm is today's standard? (the acronym)", "aes", "advanced encryption standard"),
                        _q(4, "hard", "Which ECB pitfall makes it unsafe despite using AES? (two words)", "pattern leakage", "patterns leak", "identical blocks reveal patterns", "reveals patterns"),
                        _q(5, "medium", "Which protocol lets two parties derive a shared secret over a public channel? (two words)", "diffie-hellman"),
                        _q(6, "medium", "A hash encrypted with the signer's private key is called a digital what? (one word)", "signature"),
                        _q(7, "hard", "The principle that a cryptosystem must stay secure even if everything but the key is public is named after whom? (one word)", "kerckhoffs"),
                        _q(8, "medium", "MD5 is considered broken for collision resistance. For what purpose is MD5 still commonly (wrongly) used? (one word)", "hashing", "file checksums", "checksums", "password hashing"),
                    ],
                },
                {
                    'order_index': 4,
                    'title': 'Crypto Failures and Real-World PKI',
                    'blocks': [
                        {"type": "text", "heading": "How Crypto Fails in Practice", "body": "Rarely the math — almost always the engineering: hardcoded API keys and secrets committed to repositories, keys reused across systems, non-random IVs/nonces, custom 'home-made ciphers' (always broken), and mode misuse like ECB. The 2013 Snowden-era revelations about weakened implementations, and every annual 'worst passwords and keys' report, say the same thing: process and hygiene, not algorithms, decide whether your cryptography protects anything."},
                        {"type": "text", "heading": "Password Storage Post-Mortem", "body": "LinkedIn 2012: unsalted SHA-1, millions cracked within days. Adobe 2013: encrypted (not hashed) with 3DES in ECB mode and password hints — patterns visible in the ciphertext itself. The lesson chain: plaintext < fast hash < salted fast hash < salted slow hash (bcrypt/Argon2). When you inherit a codebase, 'how are passwords stored' is a one-question security audit."},
                        {"type": "text", "heading": "Certificates in the Wild", "body": "Open any site's padlock: issuer (who vouches), validity window, SANs (which hostnames the cert covers), key algorithm. Attack surface: expired certs break services; self-signed certs train users to click through warnings; CA compromises (DigiNotar 2011 — used to MITM Iranian Gmail users) force mass re-issuance; certificate transparency logs exist precisely because silent mis-issuance was too easy."},
                        {"type": "text", "heading": "Lab Habits", "body": "Practice: hash a file, change one byte, hash again — see integrity verification in person. Decode a Base64 string, then try to 'decode' a SHA-256 hash and watch it fail — feel the difference. Read a real certificate chain. These small hands-on habits turn vocabulary into intuition, and intuition is what catches the hardcoded key at code review."},
                    ],
                    'questions': [
                        _q(1, "medium", "Which hash algorithm made LinkedIn 2012 catastrophic because it was unsalted? (the name)", "sha-1", "sha1"),
                        _q(2, "medium", "Adobe 2013 stored passwords with 3DES in which unsafe mode? (the acronym)", "ecb"),
                        _q(3, "easy", "Which two modern password hashes should you reach for instead of MD5/SHA-1? (give either)", "bcrypt", "argon2", "scrypt"),
                        _q(4, "hard", "In 2011, which Certificate Authority was compromised to MITM Gmail users in Iran? (one word)", "diginotar"),
                        _q(5, "medium", "Which public log system lets anyone detect certificates issued for a domain without the owner's knowledge? (two words)", "certificate transparency"),
                        _q(6, "medium", "Hardcoding an AES key in your source code primarily violates which practice? (two words)", "key management", "secret management"),
                    ],
                },
            ],
        },
        # ------------------------------------------------------------------
        {
            'order_index': 3,
            'title': 'Humans & the Threat Landscape',
            'description': 'Why people get tricked, what malware exists, and who is behind attacks.',
            'lessons': [
                {
                    'order_index': 1,
                    'title': 'Social Engineering — Hacking People',
                    'blocks': [
                        {"type": "text", "heading": "The Weakest Link", "body": "Firewalls don't click links. The most-patched system in any organization is the human, because humans ship with two vulnerabilities by design: we want to help, and we want to avoid trouble. Social engineering is the exploitation of trust — and it precedes every other technique in most real intrusions."},
                        {"type": "text", "heading": "The Delivery Channels", "body": "Phishing: mass email. Spear phishing: researched, personalized, far harder to spot. Whaling: executives, bigger prizes. Vishing: voice — 'IT support' calling about your account. Smishing: SMS — fake delivery notices, bank alerts. Business Email Compromise (BEC) deserves special fear: no malware, just a convincing email from 'the CEO' to finance requesting an urgent wire — billions in annual losses, the costliest attack class per incident."},
                        {"type": "text", "heading": "The Psychological Levers", "body": "Authority ('the CEO says so'), urgency ('within one hour or the account closes'), fear ('suspicious activity detected'), trust (a colleague's tone, a real-looking domain), curiosity ('your AWS bill'), and social proof ('everyone must fill this HR form'). The universal defense is a pause: verify through a second, independent channel — call the person on a known number, don't reply to the email."},
                        {"type": "text", "heading": "Spot-the-Fake Skills", "body": "Train your eye: mismatched sender domains (paypa1.com, micros0ft-support.io), hover-before-click to preview the true URL, header anomalies (reply-to ≠ from), tone that pressures instead of informing, unexpected attachments (invoice.zip), and login pages reached via email links rather than bookmarks. Scareware and fake tech-support popups are the same scam with paint: invent urgency, offer 'the fix', charge for it."},
                    ],
                    'questions': [
                        _q(1, "easy", "Mass email-based social engineering is called what? (one word)", "phishing"),
                        _q(2, "medium", "Which BEC phrase names the costliest social engineering class — fraudulent emails impersonating executives? (the acronym)", "bec", "business email compromise"),
                        _q(3, "medium", "Voice-based phishing is called what? (one word)", "vishing"),
                        _q(4, "medium", "Tailgating into a secure building exploits which human tendency? (two words)", "desire to help", "politeness", "trust", "helpfulness"),
                        _q(5, "hard", "Which single habit defeats most urgent-email scams: verify through a second what? (one word)", "channel", "method", "medium"),
                        _q(6, "medium", "Registering paypa1.com instead of paypal.com is an example of what? (one word)", "typosquatting", "typosquat"),
                    ],
                },
                {
                    'order_index': 2,
                    'title': 'Malware Families',
                    'blocks': [
                        {"type": "text", "heading": "The Three Ancestors", "body": "Virus: attaches to files, spreads when the file is run. Worm: self-propagates across networks with no user action — WannaCry's engine. Trojan: hides inside something desirable (a cracked game, a fake installer) and waits for the user to run it. Modern malware happily combines all three personalities."},
                        {"type": "text", "heading": "Ransomware and Extortion Economics", "body": "Ransomware encrypts your data and sells the key back. It evolved: single extortion (encrypt), double (encrypt + leak stolen data), triple (add a DDoS against your recovery efforts). Business model innovation, not technical innovation, drove its rise: Ransomware-as-a-Service affiliates, cryptocurrency payments, and the pivot from consumers to insured enterprises. Backups plus segmentation remain the great equalizers — if recovery is cheap, extortion is pointless."},
                        {"type": "text", "heading": "The Quiet Ones", "body": "Spyware and keyloggers harvest — credentials, keystrokes, screen contents. Rootkits and bootkits hide below the OS (or in its boot chain), surviving reinstalls. Botnets rent out thousands of zombie machines for DDoS and spam. Fileless malware lives in memory and legitimate scripting tools (PowerShell, WMI), leaving almost nothing on disk for antivirus to find. Each family implies different detections: behavioral and memory-based for the quiet ones, signatures rarely suffice."},
                        {"type": "text", "heading": "Delivery in One Sentence", "body": "Most of it arrives the boring way: a phishing attachment, a malicious ad redirect, a trojanized download, or an exploit against an unpatched service — which is why the defenses you already know (email hygiene, patching, least privilege, MFA) cut the majority of malware chains before they start."},
                    ],
                    'questions': [
                        _q(1, "easy", "Which malware type self-replicates across networks without user action? (one word)", "worm"),
                        _q(2, "easy", "Malware disguised as legitimate desirable software is called a what? (one word)", "trojan"),
                        _q(3, "medium", "Ransomware that both encrypts data and threatens to leak stolen data is called double what? (one word)", "extortion"),
                        _q(4, "medium", "Malware living only in memory and legitimate admin tools, with no files on disk, is called what? (two words)", "fileless malware", "fileless"),
                        _q(5, "medium", "A network of infected machines rented out for DDoS is called a what? (one word)", "botnet"),
                        _q(6, "hard", "Which malware class hides in boot firmware and survives OS reinstalls? (one word)", "bootkit", "rootkit"),
                    ],
                },
                {
                    'order_index': 3,
                    'title': 'Attack Types and Threat Actors',
                    'blocks': [
                        {"type": "text", "heading": "Availability and Interception Attacks", "body": "DoS: one machine exhausts a target. DDoS: thousands of bots do it simultaneously — volume-based (traffic floods) or application-layer (exhausting expensive database queries with cheap HTTP requests). MITM: the attacker sits between two parties to read or alter traffic — the reason TLS and certificate pinning exist. Know the shape of each; hands-on comes in the offensive courses."},
                        {"type": "text", "heading": "Web Attack Categories — Awareness Level", "body": "Three names you must recognize now, master later: injection (user input interpreted as code — SQL, OS commands), XSS (attacker JavaScript running in a victim's browser), broken authentication (weak logins, session flaws). They dominate the OWASP Top 10 year after year. The web pentesting specialization will make you dangerous in all three; today the goal is hearing them as categories, not magic words."},
                        {"type": "text", "heading": "Supply Chain and the Insider", "body": "SolarWinds 2020: attackers poisoned a trusted vendor's update — thousands of customers installed the backdoor themselves. Supply chain attacks exploit trust in software you didn't write. Insider threats split into malicious (stealing for money or revenge) and negligent (the employee who pastes secrets into a public AI tool). Both evade perimeter thinking entirely — you must watch behavior, not just boundaries."},
                        {"type": "text", "heading": "APTs, Zero-Days and Motivation", "body": "An APT (Advanced Persistent Threat) is a well-resourced group — usually nation-state backed — that gets in quietly and stays: custom tools, zero-days (unknown to the vendor, no patch exists) plus n-days (known but unpatched), long dwell times. Motivation predicts method: cybercrime wants money (ransomware, BEC), hacktivism wants attention (defacements, leaks), espionage wants information (quiet, patient), warfare wants disruption (grids, hospitals). Ask 'who benefits?' and you can often guess 'who'. Script kiddies run other people's tools; the APT writes them."},
                    ],
                    'questions': [
                        _q(1, "medium", "A DDoS targeting expensive database queries with cheap HTTP requests is which layer of DDoS? (one word)", "application", "application layer", "layer 7"),
                        _q(2, "medium", "A vulnerability with no vendor patch available is called a what? (two words)", "zero-day", "zero day"),
                        _q(3, "medium", "Which 2020 incident saw attackers poison a trusted vendor's software updates? (one word)", "solarwinds", "solarwinds attack"),
                        _q(4, "medium", "An employee pasting customer data into a public website is which type of insider threat? (one word)", "negligent", "negligence"),
                        _q(5, "hard", "Which threat-actor class is typically nation-state backed, patient, and focused on espionage? (the acronym)", "apt", "advanced persistent threat"),
                        _q(6, "medium", "Intercepting communication between two parties to read or alter it is called a what? (the acronym)", "mitm", "man-in-the-middle"),
                    ],
                },
                {
                    'order_index': 4,
                    'title': 'Incident Timeline — WannaCry to Colonial',
                    'blocks': [
                        {"type": "text", "heading": "Why Timelines", "body": "Incidents are stories, and learning to reconstruct them is the bridge from theory to practice: every headline incident decomposes into the building blocks this course has taught — a delivery channel, a vulnerability, a CIA impact, an actor class. Two case studies carry most of the lessons."},
                        {"type": "text", "heading": "WannaCry (May 2017)", "body": "Timeline: phishing-adjacent entry → EternalBlue (NSA exploit leaked by Shadow Brokers) spreads the worm machine-to-machine over SMB → kill-switch domain discovery slows it → 200,000+ machines across 150 countries, NHS hospitals included. CIA: availability, catastrophically; confidentiality of untouched data — intact — highlights the difference. Lessons: patch MS17-010 (out two months earlier), retire SMBv1, segmentation, and the eternal question — how long does an unapplied patch sit before the internet answers for you?"},
                        {"type": "text", "heading": "Colonial Pipeline (May 2021)", "body": "Timeline: one leaked VPN credential (no MFA) → DarkSide ransomware affiliates inside → operational halt (the pipeline shut itself down for safety) → fuel panic on the US East Coast → $4.4M paid, partly recovered by DOJ. CIA: availability of operations; confidentiality of a single credential started it. Lessons: MFA on every remote-access path, VPN gateways as crown-jewel attack surface, and OT/IT segmentation — the plant controls were never touched, but the fear of them drove the decision."},
                        {"type": "text", "heading": "Your Turn", "body": "Third incident, same drill, on your own: SolarWinds (supply chain, espionage, integrity of the update channel) or any recent ransomware case. One page: initial access, propagation, CIA impact, actor class, three controls that would have changed the story. If you can do this cleanly, you are doing incident analysis — the actual job of defenders and the opening skill of attackers."},
                    ],
                    'questions': [
                        _q(1, "medium", "Which NSA-developed SMB exploit, leaked publicly, powered WannaCry's spread? (two words)", "eternalblue"),
                        _q(2, "medium", "WannaCry's MS17-010 patch was available for how long before the outbreak? (one word — months)", "two", "2"),
                        _q(3, "medium", "Which single missing control let attackers into Colonial Pipeline's VPN? (the acronym)", "mfa", "multi-factor authentication"),
                        _q(4, "hard", "Which ransomware group hit Colonial Pipeline? (one word)", "darkside"),
                        _q(5, "medium", "Which CIA element did Colonial Pipeline's shutdown primarily violate? (one word)", "availability"),
                    ],
                },
            ],
        },
        # ------------------------------------------------------------------
        {
            'order_index': 4,
            'title': 'Risk, Ethics & Careers',
            'description': 'The vocabulary of the profession, the laws of the game, and your path into it.',
            'lessons': [
                {
                    'order_index': 1,
                    'title': 'Threat, Vulnerability, Risk, Exploit',
                    'blocks': [
                        {"type": "text", "heading": "The Four Words People Get Wrong", "body": "Threat: a potential danger (a ransomware crew, a flood). Vulnerability: a weakness (unpatched server, a reused password). Risk: the probability × impact of a threat exploiting a vulnerability — risk is the thing you manage. Exploit: the tool or code that actually abuses a vulnerability. Sentence that ties them: 'The threat of ransomware crews (threat) exploiting our unpatched VPN (vulnerability) via a public exploit (exploit) is our top risk.'"},
                        {"type": "text", "heading": "The Supporting Vocabulary", "body": "Asset: what has value. Exposure: a vulnerability that is reachable. Breach: confirmed unauthorized access to data. Incident: any event violating security policy or threatening security. Control: a safeguard — technical, administrative, or physical. Precise language is the job: a 'breach' has legal/notification consequences an 'incident' may not, and confusing them in a report confuses the response."},
                        {"type": "text", "heading": "Risk Management in Four Verbs", "body": "Identify (asset inventory, vuln scans, threat modeling) → Assess (likelihood × impact, qualitative or quantitative) → Treat: mitigate (reduce), accept (documented, with a signature), avoid (stop doing the risky thing), transfer (insurance, contracts) → Monitor (new vulns, new threats, control drift). CVSS gives vulnerability severity a number (0–10): Critical ≥9, High ≥7 — but context decides risk: a critical in an internet-facing service outranks a critical in an air-gapped lab."},
                        {"type": "text", "heading": "Vulnerability Management Loop", "body": "Discover (scan/assess) → Prioritize (CVSS + reachability + asset value) → Remediate (patch, configure, or compensate) → Verify (re-scan) → Report (trends, SLAs). The lifecycle never ends — which is the point: security is a process you run, not a state you reach. Memorize the loop; every SOC and pentest report you will ever write rides on it."},
                    ],
                    'questions': [
                        _q(1, "easy", "A weakness in a system is called a what? (one word)", "vulnerability"),
                        _q(2, "easy", "A potential danger that could exploit a weakness is called a what? (one word)", "threat"),
                        _q(3, "medium", "Risk is commonly expressed as the product of likelihood and what? (one word)", "impact"),
                        _q(4, "medium", "Code that actually abuses a vulnerability is called an what? (one word)", "exploit"),
                        _q(5, "medium", "In CVSS, which band starts at 9.0? (one word)", "critical"),
                        _q(6, "hard", "Which risk-treatment option is buying cyber insurance? (one word)", "transfer"),
                    ],
                },
                {
                    'order_index': 2,
                    'title': 'Secure Design Principles',
                    'blocks': [
                        {"type": "text", "heading": "The Big Six", "body": "Least privilege — minimum rights, always. Defense in depth — layered controls; assume each layer fails. Fail securely — an error must close the door, never open it (the exception that returns 'access granted' is a breach). Complete mediation — check every access to every object, every time, not just the first. Keep it simple — complexity hides bugs (KISS). Psychological acceptability — security that is unusable gets bypassed by its own users."},
                        {"type": "text", "heading": "Never Trust User Input", "body": "The single most productive rule in application security: every byte from outside is hostile until validated. Injection, XSS, path traversal, deserialization bugs — all boil down to input trusted too much. Related: security by obscurity (relying on secrecy of design) is not security — hidden endpoints, renamed admin pages, and 'nobody knows that URL' fail the moment they are discovered."},
                        {"type": "text", "heading": "Zero Trust and Security by Design", "body": "Zero trust: 'never trust, always verify' — no network location is implicitly trusted; every request authenticates and authorizes (identity becomes the perimeter; you met this in the Windows course). Security by design means controls live in the architecture from day one — the login flow designed with rate limiting, MFA, and logging costs less and works better than the same features bolted on after launch."},
                        {"type": "text", "heading": "OWASP Top 10 and Data Classification", "body": "The OWASP Top 10 is the industry's awareness list of the most critical web application risks — Broken Access Control, Cryptographic Failures, Injection at its recent top. You should know what it is and skim the categories; the web pentesting course will make you dangerous in them. Data classification (public → internal → confidential → secret) drives everything downstream: encryption, retention, access rules — you cannot protect what you have not classified."},
                        {"type": "text", "heading": "Privacy vs Security", "body": "Security protects data from unauthorized access; privacy governs the rights of people over data about them — collection limits, purpose, deletion. You can be perfectly secure and still privacy-hostile (extensive monitoring without consent). Regulations (GDPR and its descendants) turn privacy failures into fines, which is why security teams and privacy teams share an org chart."},
                    ],
                    'questions': [
                        _q(1, "medium", "An exception handler that returns 'access granted' on error violates which principle? (two words)", "fail securely", "fail secure", "fail-safe defaults"),
                        _q(2, "medium", "Checking permissions on every access, not just the first, is called complete what? (one word)", "mediation"),
                        _q(3, "easy", "Relying on the secrecy of a design rather than its strength is security by what? (one word)", "obscurity"),
                        _q(4, "medium", "'Never trust, always verify' is the slogan of which architecture? (two words)", "zero trust", "zero-trust"),
                        _q(5, "easy", "Every byte coming from outside the system should be treated as what until validated? (one word)", "hostile", "untrusted", "malicious"),
                        _q(6, "medium", "Which published list raises awareness of the most critical web application security risks? (three words)", "owasp top 10", "owasp top ten"),
                        _q(7, "medium", "Sorting data into public, internal, confidential and secret is called data what? (one word)", "classification"),
                    ],
                },
                {
                    'order_index': 3,
                    'title': 'Ethics, Law and the Rules of the Game',
                    'blocks': [
                        {"type": "text", "heading": "The Hats", "body": "White hat: authorized security work — pentesters, auditors. Black hat: unauthorized — criminals. Grey hat: technically unauthorized but not malicious — finding flaws and disclosing them without permission. The industry pays for the first, prosecutes the second, and argues endlessly about the third. Your professional identity is built on which side of authorization you operate on — keep it bright-line clear."},
                        {"type": "text", "heading": "Authorization Is Everything", "body": "Unauthorized access is a crime nearly everywhere (computer fraud laws: CFAA in the US, Computer Misuse Act in the UK, equivalents across the world). The golden rule for learning: attack only your own lab, or targets you have written permission to test. 'I was just testing' has never once been a defense. Scope and written authorization define what is allowed — anything outside them is illegal, however harmless it felt."},
                        {"type": "text", "heading": "Responsible Disclosure and Bug Bounties", "body": "Found a real flaw in someone's product? Responsible disclosure: report privately, give a reasonable fix window, coordinate publication. Bug bounty programs formalize this: rules define scope (what you may test), rewards define severity, and outside the rules you are just a trespasser with a hobby. Reading real disclosure reports is one of the best free educations in security thinking — the good ones read like detective stories with proof-of-concepts."},
                        {"type": "text", "heading": "The Team Colors", "body": "Red team: offense — emulates real adversaries to test defenses. Blue team: defense — detects and responds. Purple team: the collaboration — red's techniques feeding blue's detections continuously. Pentest usually means scoped, time-boxed testing of defined targets; red teaming means unconstrained simulation of a real adversary. Know the vocabulary before the job titles confuse you."},
                    ],
                    'questions': [
                        _q(1, "easy", "Which hat does authorized security testing? (one word)", "white", "white hat"),
                        _q(2, "medium", "Reporting a flaw privately and giving the vendor time to fix before publication is called what disclosure? (one word)", "responsible", "coordinated"),
                        _q(3, "easy", "The golden rule of practice: attack only your own what? (one word)", "lab", "systems"),
                        _q(4, "medium", "Which team color defends and responds? (one word)", "blue"),
                        _q(5, "medium", "Which team color emulates real adversaries to test defenses? (one word)", "red"),
                        _q(6, "medium", "The collaboration where red team techniques continuously improve blue team detections is called what team? (one word)", "purple"),
                        _q(7, "medium", "True or false: 'I was only testing security' is a valid legal defense for unauthorized access.", "false"),
                    ],
                },
                {
                    'order_index': 4,
                    'title': 'Careers, Certifications and Your Roadmap',
                    'blocks': [
                        {"type": "text", "heading": "The Career Families", "body": "Defensive: SOC analyst (entry — watching detections), incident responder, threat hunter, DFIR specialist. Offensive: pentester, red teamer, bug bounty hunter. Governance: GRC analyst, auditor, CISO track. Specialty: cloud security, AppSec, malware analysis. Every family reads the same fundamentals you just learned — the difference is which side of the controls you work."},
                        {"type": "text", "heading": "The Certification Ladder", "body": "Commonly: CompTIA Security+ for vocabulary and breadth (the standard HR filter) → then specialize: CEH/eCPT offensively, CySA+ defensively, BTL1/Blue Team Level 1 for blue teams, CISSP later (it is a management-level exam requiring experience). Certifications open doors; they do not make you capable — labs and platforms do that part."},
                        {"type": "text", "heading": "Learning Platforms and Habits", "body": "TryHackMe for guided early reps, HackTheBox for harder unguided practice, OverTheWire for wargames fundamentals, and this platform's paths for structure. The habit that separates learners who make it: write-ups. Document every box, every room, every CTF: what you tried, what failed, what worked, why. Your notes compound; your memory does not. A public blog of write-ups is also the strongest entry-level portfolio that exists."},
                        {"type": "text", "heading": "Your Six-Month Plan", "body": "Finish this course's siblings (Linux, Networking, Windows) → pick a lane for depth (offense or defense) → one guided platform track + one unguided practice target per month → one write-up per week, published → map to a certification at month four, sit it at six. Revisit this plan monthly; adjust with evidence (what did you actually finish?), not enthusiasm. The people who make it are not the ones who start fastest — they are the ones still writing write-ups in month six."},
                    ],
                    'questions': [
                        _q(1, "easy", "Which entry-level certification is the standard HR filter for security vocabulary? (two words)", "security+", "comptia security+"),
                        _q(2, "medium", "Watching detections in a SOC is typically which career path's entry role? (two words)", "soc analyst"),
                        _q(3, "medium", "Which later-stage certification requires professional experience and targets management-level knowledge? (the acronym)", "cissp"),
                        _q(4, "medium", "Documenting every challenge you solve — what you tried, what worked, why — is called writing what? (plural)", "write-ups", "writeups"),
                        _q(5, "hard", "Which platform is known for harder, unguided practice boxes compared to TryHackMe's guided rooms? (the acronym)", "htb", "hackthebox", "hack the box"),
                        _q(6, "medium", "Offensive certifications like CEH or eCPT map to which career family? (one word)", "offensive", "offense"),
                    ],
                },
            ],
        },
    ],
}
