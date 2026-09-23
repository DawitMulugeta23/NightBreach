"""
Seeds the Learning Paths hierarchy: Paths → Rooms → Lessons → Questions.
Regenerated from database state. Idempotent — re-running updates by slug/order.
"""
import asyncio
import hashlib
import uuid

from sqlalchemy import select

from db.session import AsyncSessionLocal
from db.models import (
    LearningPath, Room, Lesson, LessonQuestion, QuestionType, QuestionDifficulty,
)


def _hash_answer(answer: str) -> str:
    return hashlib.sha256(answer.strip().lower().encode()).hexdigest()


def _hash_answers(answers) -> str:
    """Store one or more acceptable answers joined by '|', each hashed."""
    if isinstance(answers, str):
        answers = [answers]
    return "|".join(_hash_answer(a) for a in answers if a)


def _flag(value: str) -> str:
    """Wrap a plaintext value in the NB{...} flag format."""
    return f"NB{{{value}}}"


def _resolve_answer_hash(q_data: dict) -> str:
    """Return the answer hash for a question, from 'flag' if present, else 'answer_hash'."""
    if "flag" in q_data:
        return _hash_answers(_flag(q_data["flag"]))
    return q_data["answer_hash"]


SEED_DATA = [
    {
        'slug': 'linux-fundamentals',
        'title': 'Linux Fundamentals',
        'description': 'Master the Linux command line from first principles.',
        'icon': '/linuxlogo.jpeg',
        'order_index': 1,
        'rooms': [
            {
                'order_index': 1,
                'title': 'Fundamental',
                'description': 'Absolute basics: navigating, viewing, and managing files.',
                'lessons': [
                    {
                        'order_index': 1,
                        'title': 'Linux History & What is an OS/Kernel',
                        'blocks': [{"type": "text", "heading": "Before Linux: Unix", "body": "In 1969, engineers at Bell Labs (AT&T) built an operating system called Unix. It introduced ideas that are still core to Linux today: everything is a file, small programs that do one thing well, and a hierarchical filesystem. Unix became hugely influential, but it was proprietary \u2014 companies had to pay for licenses to use or modify it."}, {"type": "text", "heading": "The GNU Project", "body": "In 1983, Richard Stallman started the GNU Project with a goal: build a completely free (as in freedom) Unix-like operating system. Over the next decade, GNU produced excellent free tools \u2014 a compiler, a text editor, a shell, and core utilities like ls, cat, and grep. But GNU was missing one critical piece: a kernel, the core program that actually talks to the hardware."}, {"type": "text", "heading": "Linus Torvalds and the Kernel", "body": "In 1991, a Finnish student named Linus Torvalds started writing his own kernel as a hobby project, posting about it on a newsgroup. That kernel became Linux. Combined with GNU's tools, it formed a complete, free operating system \u2014 technically 'GNU/Linux', though most people just call it Linux."}, {"type": "text", "heading": "What is a Kernel?", "body": "The kernel is the core program of an operating system. It manages the CPU (deciding which program runs when), memory (allocating and protecting RAM for each program), and devices (translating requests from programs into hardware instructions for disks, network cards, keyboards, etc). Every program you run ultimately asks the kernel for permission to use these resources."}, {"type": "text", "heading": "What is an Operating System?", "body": "An operating system is the kernel plus everything needed to make it usable: a shell to type commands into, core utilities (ls, cp, grep), system services, and often a package manager. The kernel alone can't do anything useful by itself \u2014 it needs this surrounding software."}, {"type": "text", "heading": "What is a Distribution (Distro)?", "body": "A distribution is a complete, ready-to-install package built around the Linux kernel: the kernel itself, GNU tools, a package manager, default configuration, and often a desktop environment. Ubuntu, Debian, Fedora, and Arch are all different distributions that share the same underlying Linux kernel but differ in how they're packaged, configured, and maintained."}, {"type": "text", "heading": "Why This Matters for You", "body": "Everything you'll learn in this course works because of this layered design: your commands (ls, cd, grep) are just programs. They ask the kernel to do things on their behalf. Understanding this separation \u2014 kernel vs OS vs distro \u2014 will make every future lesson click faster, because you'll know which layer a concept belongs to."}],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'In what year did Linus Torvalds first release the Linux kernel?',
                                'answer_hash': '8e9b669109df89620b94f2387dc53206a82ddc71d658f8f7a2b3a9b417370d3e',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'What is the name of the project Richard Stallman started in 1983 to build free Unix-like tools?',
                                'answer_hash': 'ab137b027d5988d44880bdf94489a66c9e06d5861a04b54a72ab344ae7534024',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 2,
                        'title': 'Why the Shell — CLI vs GUI',
                        'blocks': [
                            {"type": "text", "heading": "Two Ways to Talk to a Computer", "body": "A graphical interface (GUI) lets you point and click; a command-line interface (CLI) lets you type. Point-and-click feels easier at first, but it has a hard ceiling: you can only do what someone drew a button for, one click at a time. The shell has no ceiling — every capability of the system is reachable, and actions compose into larger ones."},
                            {"type": "text", "heading": "Why the Shell Wins for Servers", "body": "The machines you'll administer — and attack — rarely have screens at all. Servers run headless in datacenters and clouds, managed entirely over SSH in plain text. And text is automatable: a sequence of shell commands can be saved, replayed, scheduled, and shared exactly. You can't copy-paste a series of mouse clicks."},
                            {"type": "text", "heading": "The Shell Is Also a Programming Language", "body": "Everything you're learning in this course — pipes, redirection, variables, loops — turns the shell from a command runner into a scripting language. That's why the shell is the foundation of automation: a backup job is a script, a monitoring alert is a script, an attack tool prototype is often just a clever one-liner."},
                            {"type": "text", "heading": "Which Distribution?", "body": "A distribution is the Linux kernel plus a curated set of tools and a package manager: Ubuntu and Debian use apt, Red Hat and Fedora use dnf, Arch uses pacman. Servers typically run Ubuntu Server or Debian; security-focused live distributions like Kali (the family this platform's sandbox resembles) bundle offensive tooling on top of Debian. The commands in this course are identical across all of them."},
                            {"type": "text", "heading": "Your Lab", "body": "To practice: install WSL on a Windows machine, run Ubuntu Server or Desktop in VirtualBox, or simply use this platform's browser sandbox — a real Linux shell with nothing to install. Keeping a personal cheat sheet of commands as you learn is the single highest-value habit for this whole course."},
                            {"type": "practice", "command": "echo $SHELL", "instructions": "Print which shell program you're running right now."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'What is the text-based interface for typing commands called, as opposed to a graphical one? (three-letter abbreviation)',
                                'answer_hash': '99bb88401742848e032fd6f51709415fb6be169a72d2e5d7fc44289255160d3c',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which command prints text to the terminal — and is usually the first command inside a script?',
                                'answer_hash': '092c79e8f80e559e404bcf660c48f3522b67aba9ff1484b0367e1a4ddef7431d',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which encrypted protocol gives you a text shell on a remote machine?',
                                'answer_hash': '7f5a55cf3f88be936fb9440249cb449f3067ccee4b525d0027dc9278a29c32c1',
                                'setup_script': None,
                            },
                            {
                                'order_index': 4,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which single flag makes ls print the long, detailed listing? (e.g. ls -?)',
                                'answer_hash': '8d29a0f35918ca625667b2858e1c366e227ecbb424c5b30d008a1b2ec709e6d2',
                                'setup_script': None,
                            },
                            {
                                'order_index': 5,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which syntax captures the output of a command so it can be stored in a variable? (the modern form)',
                                'answer_hash': '2617eed3a09b68d29f36a9fc201579857a5dceece46923f9f868bbadd887a196|3daefd69f5d3d9242cfdea2037316c852eab5e38464b44c42012da10c2c4a0df',
                                'setup_script': None,
                            },
                            {
                                'order_index': 6,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Before a script can be run directly, which chmod symbolic mode adds execute permission for everyone? (e.g. chmod ? file.sh)',
                                'answer_hash': '753e9f854e2c64006dfe68087058f4b58efe4398dbc144b1b41bc81afc3f4948|04a6fb16934512861d5643dc9a5f8e7881cf42630a6f23699a6bca66d01ffbf9',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 3,
                        'title': 'Who Am I? — whoami',
                        'blocks': [{"type": "text", "heading": "The whoami Command", "body": "whoami prints the username of the account you are currently logged in as. It takes no arguments, does no configuration \u2014 it simply answers one question: who is running this shell right now?"}, {"type": "text", "heading": "Why Identity Matters on Linux", "body": "Linux is a multi-user system at its core, even when only one person uses a machine. Every process, every file, every action is tied to a specific user account. Two users can have completely different permissions, home directories, and access levels on the exact same machine."}, {"type": "text", "heading": "The root User", "body": "Every Linux system has one special account called root \u2014 the superuser, with unrestricted access to everything on the system. Running commands as root is powerful but dangerous: a typo that's harmless as a normal user can destroy a system when run as root. Knowing whether whoami says 'root' or a regular username is one of the first safety checks you should develop as a habit."}, {"type": "text", "heading": "Related Commands", "body": "id gives more detail than whoami \u2014 it shows your user ID (UID), group ID (GID), and all groups you belong to. logname shows the name you originally logged in with, which can differ from whoami if you've switched users with su or sudo."}, {"type": "practice", "command": "whoami", "instructions": "Start the machine and run whoami in the terminal. Note the exact output \u2014 you'll be asked for it below."}],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'terminal',
                                'difficulty': 'easy',
                                'prompt': 'Run whoami in the terminal. What is the exact output?',
                                'answer_hash': 'efd66a42c2df19aa388e9a5ec6d83ad1ddde6e30efc3880f7c79b76b47c3c7c9',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'What is the name of the special superuser account on every Linux system?',
                                'answer_hash': '4813494d137e1631bba301d5acab6e7bb7aa74ce1185d456565ef51d737677b2',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 4,
                        'title': 'Where Am I? — pwd',
                        'blocks': [{"type": "text", "heading": "pwd \u2014 Print Working Directory", "body": "pwd prints the absolute path of the directory you are currently 'in'. Every terminal session has a current location in the filesystem \u2014 pwd tells you exactly where that is, with no ambiguity."}, {"type": "text", "heading": "The Root of Everything", "body": "Linux has a single, unified filesystem tree, starting at / (called 'root' \u2014 not to be confused with the root user). Every file and directory on the system, no matter which physical disk it's actually stored on, appears somewhere under this one tree. There's no concept of 'C: drive' like on Windows."}, {"type": "text", "heading": "Your Home Directory", "body": "Each user account has a home directory, typically /home/<username>, where their personal files live. When you log in, your shell usually starts here. It's the one place you're guaranteed to have full read/write access without needing special permissions."}, {"type": "text", "heading": "Absolute Paths", "body": "An absolute path always starts with / and describes a location starting from the root of the filesystem, regardless of where you currently are. /home/dave/notes.txt means exactly the same file no matter what directory you run it from."}, {"type": "practice", "command": "pwd", "instructions": "Run pwd in the terminal. It should print your home directory path, starting with /home/."}],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'What character does every absolute path in Linux start with?',
                                'answer_hash': '8a5edab282632443219e051e4ade2d1d5bbc671c781051bf1437897cbdfea0f1',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'terminal',
                                'difficulty': 'easy',
                                'prompt': 'Run pwd in the terminal. Paste the full output exactly as shown.',
                                'answer_hash': '190afcb75ef04afe4adf3ca764370be7c544d6388674d2cdc9af93458b05cd2f',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 5,
                        'title': 'Listing Files — ls',
                        'blocks': [{"type": "text", "heading": "ls \u2014 List Directory Contents", "body": "ls shows you the files and directories inside your current location (or a location you specify). It's one of the most frequently typed commands on any Linux system."}, {"type": "text", "heading": "Useful Flags", "body": "ls -l gives a 'long' listing: permissions, owner, group, size, and modification date for each item. ls -a shows 'all' files, including hidden ones (which start with a dot). ls -h, combined with -l, shows sizes in human-readable form (like 4.0K instead of 4096). These flags can be combined: ls -lah is extremely common."}, {"type": "text", "heading": "Reading a Long Listing", "body": "A line from ls -l looks like: -rw-r--r-- 1 dave dave 220 Mar 31 2024 .bashrc. The first character indicates the type (- for file, d for directory). The next nine characters are three permission groups: owner, group, others. Then comes the owner name, group name, file size, and last-modified date."}, {"type": "text", "heading": "Listing a Specific Location", "body": "By default ls lists your current directory, but you can point it anywhere: ls /etc lists the contents of /etc without you needing to actually move there first."}, {"type": "practice", "command": "ls -la", "instructions": "Run ls -la in your home directory and observe the full listing, including hidden dotfiles."}],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which ls flag shows hidden (dotfile) entries?',
                                'answer_hash': 'c274891790345c56cef3b53c026bdc48150948fa60c56306073d6fea7766ad6a',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': "Which ls flag produces the detailed 'long' listing format?",
                                'answer_hash': '8d29a0f35918ca625667b2858e1c366e227ecbb424c5b30d008a1b2ec709e6d2',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 6,
                        'title': 'Reading Files — cat',
                        'blocks': [{"type": "text", "heading": "cat \u2014 Concatenate and Print", "body": "cat prints the entire contents of one or more files directly to your terminal. Its name comes from 'concatenate' \u2014 its original purpose was joining files together, but it's most commonly used just to quickly view a file's contents."}, {"type": "text", "heading": "When cat Isn't Ideal", "body": "cat dumps everything at once with no scrolling control, which is fine for small files but unwieldy for anything long. For big files, less (a pager that lets you scroll and search) is usually a better choice \u2014 you'll meet it in a later lesson."}, {"type": "text", "heading": "Multiple Files at Once", "body": "cat file1.txt file2.txt prints both files' contents back to back, in the order given. This is genuinely useful for quickly combining small config snippets or logs."}, {"type": "text", "heading": "Redirecting Output", "body": "Combined with the > operator (covered in a later lesson), cat can also be used to quickly create a file: cat > newfile.txt lets you type content directly, ending with Ctrl+D."}, {"type": "practice", "command": "cat .bashrc", "instructions": "Run cat .bashrc in your home directory to view the contents of your shell configuration file."}],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': "What word does the name 'cat' come from?",
                                'answer_hash': '0afe756cd1e815034cfaf42660ea13c6eec402a3b9c4359838ed90dfb89ad2c3',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 7,
                        'title': 'Creating Files & Directories — touch, mkdir',
                        'blocks': [{"type": "text", "heading": "touch \u2014 Create an Empty File", "body": "touch creates a new, empty file if it doesn't already exist. If the file already exists, touch instead updates its 'last modified' timestamp to the current time without changing its contents \u2014 that was actually its original purpose."}, {"type": "text", "heading": "mkdir \u2014 Make Directory", "body": "mkdir creates a new, empty directory. Trying to create a directory that already exists will produce an error, unless you use the -p flag."}, {"type": "text", "heading": "Creating Nested Directories with -p", "body": "By default, mkdir fails if the parent directory doesn't exist yet \u2014 mkdir a/b/c fails if a doesn't exist. mkdir -p a/b/c creates all three levels at once, and also silently succeeds if some of them already exist. This is the version most people actually want to use."}, {"type": "text", "heading": "Naming Conventions", "body": "Linux filenames can contain spaces and most characters, but spaces make command-line work painful (you have to quote or escape them). Convention favors lowercase names with hyphens or underscores instead of spaces, e.g. my-notes.txt rather than 'my notes.txt'."}, {"type": "practice", "command": "mkdir -p projects/notes && touch projects/notes/todo.txt", "instructions": "Create a nested directory structure and an empty file inside it in one line."}],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': "Which mkdir flag lets you create nested parent directories that don't exist yet?",
                                'answer_hash': '567479c447e472328522a1d759aabb9b579e4522a6da547c983d29e94c1604c2',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'terminal',
                                'difficulty': 'easy',
                                'prompt': 'Create a directory called practice_dir in your home directory using mkdir, then run ls to confirm it exists. What command did you use to create it? (just the command)',
                                'answer_hash': '96dbad55cf590d1cdfe2a3496bab81073ccd30d544a4e22223c7b19892d92622',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 8,
                        'title': 'Copying, Moving & Deleting — cp, mv, rm',
                        'blocks': [{"type": "text", "heading": "cp \u2014 Copy Files", "body": "cp source destination copies a file, leaving the original in place. cp -r is required to copy an entire directory recursively \u2014 without -r, cp refuses to copy directories."}, {"type": "text", "heading": "mv \u2014 Move or Rename", "body": "mv source destination moves a file to a new location \u2014 and since 'renaming' is really just 'moving to a new name in the same directory', mv is also how you rename files: mv oldname.txt newname.txt."}, {"type": "text", "heading": "rm \u2014 Remove Files", "body": "rm deletes files permanently \u2014 there is no Recycle Bin on the command line. rm -r deletes directories and their contents recursively. rm -f forces deletion without confirmation prompts. rm -rf combines both and is one of the most dangerous command combinations in Linux \u2014 always double-check your path before running it."}, {"type": "text", "heading": "A Word of Caution", "body": "Unlike graphical file managers, none of these commands ask 'are you sure?' by default, and there's no undo. Before running rm -rf on anything, it's good practice to first run ls on the same path to confirm exactly what you're about to delete."}, {"type": "practice", "command": "cp projects/notes/todo.txt projects/notes/todo-backup.txt", "instructions": "Make a backup copy of a file, then use mv to rename it, then rm to delete the original."}],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which flag must you add to cp to copy an entire directory recursively?',
                                'answer_hash': '1e1caaf8cf28cb0243175a8dd26a3fc0d8f2c5527c661586bb816e57b9919be2',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which single command is used both to move a file AND to rename it?',
                                'answer_hash': 'd1829078fe03f2ec5f692c7a217859409b6822240625c10282bb022888657148',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 9,
                        'title': 'Getting Help — man and --help',
                        'blocks': [{"type": "text", "heading": "man \u2014 Manual Pages", "body": "Almost every command on Linux ships with a manual page, accessed with man <command>, e.g. man ls. Manual pages describe every flag and option in detail and are the authoritative reference \u2014 often more complete than anything you'll find online."}, {"type": "text", "heading": "Navigating man Pages", "body": "man opens content in a pager (usually less). Use the arrow keys or spacebar to scroll, / followed by a search term to search within the page, and q to quit back to your shell."}, {"type": "text", "heading": "--help \u2014 Quick Reference", "body": "Most commands also support a --help flag (e.g. ls --help) that prints a brief summary of options directly to the terminal, without opening a pager. It's faster than man for a quick reminder of a flag you've forgotten."}, {"type": "text", "heading": "Building the Habit", "body": "New Linux users often reach for a search engine before trying man or --help. Learning to check the manual first is genuinely faster once you're used to it, and it works even without an internet connection \u2014 which matters more than it might seem on a remote server."}, {"type": "practice", "command": "man ls", "instructions": "Open the manual page for ls, scroll through a few options, then press q to quit."}],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'What key do you press to quit out of a man page?',
                                'answer_hash': '8e35c2cd3bf6641bdb0e2050b76932cbb2e6034a0ddacc1d9bea82a6ba57f7cf',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 10,
                        'title': 'Hidden Files & Wildcards',
                        'blocks': [{"type": "text", "heading": "Hidden (Dot) Files", "body": "Any file or directory whose name starts with a dot (.) is 'hidden' from a plain ls listing. This isn't a security feature \u2014 it's a convention to keep configuration files (like .bashrc, .gitignore) out of the way during normal browsing. ls -a reveals them."}, {"type": "text", "heading": "The Wildcard *", "body": "The asterisk * matches any sequence of characters in a filename. ls *.txt lists every file ending in .txt in the current directory. rm *.log would delete every file ending in .log \u2014 a powerful and dangerous pattern."}, {"type": "text", "heading": "The Wildcard ?", "body": "The question mark ? matches exactly one character. file?.txt would match file1.txt and fileA.txt, but not file10.txt (too many characters) or file.txt (too few)."}, {"type": "text", "heading": "Combining Wildcards", "body": "Wildcards can be combined and placed anywhere in a pattern: *.tar.gz matches any gzip-compressed tarball, backup_*.sql matches any file starting with backup_ and ending in .sql."}, {"type": "practice", "command": "touch a.txt b.txt c.log && ls *.txt", "instructions": "Create a few files with different extensions, then use a wildcard to list only the .txt ones."}],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which wildcard character matches any sequence of characters in a filename?',
                                'answer_hash': '684888c0ebb17f374298b65ee2807526c066094c701bcc7ebbe1c1095f494fc1',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which wildcard character matches exactly one character?',
                                'answer_hash': '8a8de823d5ed3e12746a62ef169bcf372be0ca44f0a1236abc35df05d96928e1',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 11,
                        'title': 'Command History & Shortcuts',
                        'blocks': [{"type": "text", "heading": "Command History", "body": "Bash remembers every command you type, in order. Press the Up arrow to cycle backward through previous commands, Down to go forward again. This alone saves enormous amounts of retyping."}, {"type": "text", "heading": "The history Command", "body": "Running history prints your entire recorded command history with line numbers. You can re-run a specific past command with !123 (where 123 is its history number), or the most recent command again with !!."}, {"type": "text", "heading": "Tab Completion", "body": "Pressing Tab while typing a command or filename asks the shell to auto-complete it. If there's only one possible match, it completes immediately; if there are several, pressing Tab twice lists all the options. This dramatically reduces typos on long filenames."}, {"type": "text", "heading": "Useful Shortcuts", "body": "Ctrl+C cancels the currently running command. Ctrl+R starts a reverse search through your history \u2014 start typing a fragment of a past command and it jumps to the most recent match. Ctrl+L clears the screen (same as typing clear)."}, {"type": "practice", "command": "history | tail -5", "instructions": "Run history and view your last five commands. Try pressing the Up arrow a few times in the terminal to cycle through them."}],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'What keyboard shortcut starts a reverse search through your command history?',
                                'answer_hash': '953626bc62ad9183155ac9e2a45b487b5d87773f97ccf2509d92006a5e49ca86',
                                'setup_script': None,
                            },
                        ],
                    },
                ],
            },
            {
                'order_index': 2,
                'title': 'Intermediate',
                'description': 'Text processing, permissions, and process management.',
                'lessons': [
                    {
                        'order_index': 1,
                        'title': 'Searching Text — grep',
                        'blocks': [{"type": "text", "heading": "grep \u2014 Search Inside Files", "body": "grep searches the contents of files (or piped input) for lines matching a pattern, and prints those lines. It's one of the most-used tools in all of Linux \u2014 for log analysis, code searching, and filtering command output."}, {"type": "text", "heading": "Basic Usage", "body": "grep pattern file.txt prints every line in file.txt containing 'pattern'. grep is case-sensitive by default \u2014 'Error' and 'error' are treated as different strings."}, {"type": "text", "heading": "Common Flags", "body": "grep -i ignores case. grep -r searches recursively through every file in a directory tree. grep -n prefixes each match with its line number. grep -v inverts the match, printing every line that does NOT match \u2014 extremely useful for filtering out noise."}, {"type": "text", "heading": "Counting Matches", "body": "grep -c doesn't print matching lines at all \u2014 it prints a count of how many lines matched. This is often faster than piping to wc -l when you only need the number."}, {"type": "text", "heading": "Regular Expressions", "body": "grep supports basic regular expressions by default: ^ anchors to the start of a line, $ anchors to the end, . matches any single character. grep -E (or egrep) enables extended regex syntax with more powerful pattern features."}, {"type": "text", "heading": "Combining with Pipes", "body": "grep is most powerful when combined with other commands via a pipe (covered in a later lesson): ps aux | grep nginx finds running nginx processes by filtering the output of ps."}, {"type": "practice", "command": "grep -n root /etc/passwd", "instructions": "Search /etc/passwd for lines containing 'root' and show the line numbers."}],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which grep flag makes the search case-insensitive?',
                                'answer_hash': '444c8974fcf3d4d990db382d0a6ed1d69ffc4caa10da28afd7ab561fd7f27ced',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which grep flag inverts the match, printing lines that do NOT match?',
                                'answer_hash': '81c36ccd44ef18baabad6e2d87038b72d606263bd6a3432b964a872023654fff',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 2,
                        'title': 'Finding Files — find',
                        'blocks': [{"type": "text", "heading": "find \u2014 Locate Files by Criteria", "body": "find searches a directory tree for files and directories matching criteria you specify \u2014 name, size, type, modification time, and more. Unlike grep (which searches file contents), find searches for the files themselves."}, {"type": "text", "heading": "Basic Syntax", "body": "find <path> -name '<pattern>' searches starting at <path> for anything matching the name pattern. find . -name '*.txt' finds every .txt file starting from the current directory downward."}, {"type": "text", "heading": "Filtering by Type", "body": "find . -type f restricts results to regular files only. find . -type d restricts to directories only. This is useful when a name pattern could match both."}, {"type": "text", "heading": "Filtering by Size and Time", "body": "find . -size +10M finds files larger than 10 megabytes. find . -mtime -1 finds files modified within the last day. These are invaluable for cleaning up disk space or investigating recent changes."}, {"type": "text", "heading": "Acting on Results with -exec", "body": "find can run a command on every match it finds: find . -name '*.tmp' -exec rm {} \\; deletes every .tmp file found. The {} is replaced with each matched filename, and the command must end with \\;"}, {"type": "text", "heading": "find vs locate", "body": "The locate command is a faster alternative that searches a pre-built index rather than scanning the disk live \u2014 but that index can be out of date. find always reflects the current state of the filesystem, at the cost of being slower on large trees."}, {"type": "practice", "command": "find /etc -name '*.conf' -type f", "instructions": "Search /etc for all configuration files ending in .conf."}],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which find flag restricts results to regular files only (not directories)?',
                                'answer_hash': 'f8347f63803b4206159a1f9b1050148f64f161b2ef2b58cdedae00c10aefee73',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 3,
                        'title': 'Permissions Deep Dive — chmod',
                        'blocks': [{"type": "text", "heading": "The Three Permission Types", "body": "Every file has three types of permission: read (r) \u2014 view contents; write (w) \u2014 modify contents; execute (x) \u2014 run as a program, or enter a directory. These apply separately to three categories of people: the owner, the group, and everyone else (others)."}, {"type": "text", "heading": "Reading Permission Strings", "body": "In ls -l output, -rwxr-xr-- breaks down as: owner has rwx (read/write/execute), group has r-x (read/execute, no write), others have r-- (read only). The leading - means it's a regular file (d would mean directory)."}, {"type": "text", "heading": "Symbolic Mode", "body": "chmod u+x file adds execute permission for the owner (user). chmod g-w file removes write from the group. chmod o=r file sets others to read-only, replacing whatever was there. u, g, o, a (all) combine with +, -, = and r, w, x."}, {"type": "text", "heading": "Numeric (Octal) Mode", "body": "Each permission has a numeric value: read=4, write=2, execute=1. Adding them gives one digit per category: rwx=7, rw-=6, r-x=5, r--=4. chmod 644 file gives the owner read+write, and group/others read-only \u2014 an extremely common setting for regular files. chmod 755 is the equivalent common setting for executable scripts and directories."}, {"type": "text", "heading": "Recursive Changes", "body": "chmod -R 755 mydir/ applies the permission change to the directory AND everything inside it, recursively. Use this carefully \u2014 it's easy to accidentally make files executable that shouldn't be, or lock yourself out of files you need."}, {"type": "text", "heading": "Why This Matters for Security", "body": "Incorrect permissions are one of the most common real-world security mistakes \u2014 a world-writable config file, or a private key readable by everyone, can compromise an entire system. Understanding chmod precisely, rather than copy-pasting numbers you don't understand, is a genuine security skill."}, {"type": "practice", "command": "touch script.sh && chmod 755 script.sh && ls -l script.sh", "instructions": "Create a file, make it executable for everyone, and verify the permission string with ls -l."}],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': "What numeric value represents read+write+execute permission (rwx) in chmod's octal mode?",
                                'answer_hash': '7902699be42c8a8e46fbbb4501726517e86b22c56a189f7625a6da49081b2451',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'What common chmod numeric mode gives the owner read+write and everyone else read-only?',
                                'answer_hash': '87e50b28705900bb064d1e9df1bd6cf55a7efa01cc16c6cf0703f491a1f13d44',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 4,
                        'title': 'Ownership — chown, chgrp',
                        'blocks': [{"type": "text", "heading": "chown \u2014 Change Owner", "body": "Every file has exactly one owning user and one owning group. chown newowner file changes the owning user. Only root (or the current owner, in limited cases) can change ownership \u2014 a regular user can't give away files they don't own to someone else."}, {"type": "text", "heading": "Changing Both User and Group", "body": "chown user:group file changes both the owner and the group in one command. chown user: file (with a trailing colon, no group name) changes only the owner but leaves the group unchanged if you omit the group name entirely and just use chown user file."}, {"type": "text", "heading": "chgrp \u2014 Change Group Only", "body": "chgrp newgroup file changes only the group ownership, leaving the user owner untouched. It's functionally equivalent to chown :newgroup file, just more explicit about intent."}, {"type": "text", "heading": "Recursive Ownership Changes", "body": "chown -R user:group directory/ applies the change to the directory and everything inside it. This is common when moving a project between users, or fixing ownership after files were accidentally created as root."}, {"type": "text", "heading": "Ownership vs Permissions", "body": "Ownership (chown) determines WHO the permission categories (owner/group/others) actually refer to for a given file. Permissions (chmod) determine WHAT each category can do. They work together: chmod 600 file combined with correct chown ownership means only that specific user can read or write the file at all."}, {"type": "practice", "command": "touch secret.txt && ls -l secret.txt", "instructions": "Create a file and check who owns it with ls -l \u2014 the third and fourth columns show user and group."}],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'What command changes ONLY the group ownership of a file, without touching the user owner?',
                                'answer_hash': 'db31a74202f83329237ae92c40d1601f1ce39b2a368c3b5d77848900388e7213',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 5,
                        'title': 'Redirection & Pipes',
                        'blocks': [{"type": "text", "heading": "Standard Streams", "body": "Every process has three data streams by default: stdin (standard input, where it reads from \u2014 usually your keyboard), stdout (standard output, where normal results go \u2014 usually your screen), and stderr (standard error, where error messages go, also usually your screen)."}, {"type": "text", "heading": "Redirecting Output with >", "body": "command > file.txt sends stdout into a file instead of the screen, overwriting the file if it already exists. echo hello > greeting.txt creates a file containing 'hello'."}, {"type": "text", "heading": "Appending with >>", "body": "command >> file.txt appends output to the end of a file instead of overwriting it. This is what you want when adding new log lines or accumulating results across multiple runs."}, {"type": "text", "heading": "Redirecting Input with <", "body": "command < file.txt feeds a file's contents into a command's stdin, as if you had typed it. Less common than output redirection, but useful for feeding data into programs that read from stdin."}, {"type": "text", "heading": "Pipes with |", "body": "The pipe | connects the stdout of one command directly to the stdin of the next, without any intermediate file. ls -la | grep '.txt' lists files and filters them through grep in a single line, entirely in memory."}, {"type": "text", "heading": "Chaining Multiple Pipes", "body": "Pipes can be chained indefinitely: cat access.log | grep ERROR | sort | uniq -c reads a log, filters for errors, sorts them, then counts duplicate lines. Building up a pipeline step by step, checking output at each stage, is a core Linux workflow skill."}, {"type": "practice", "command": "ls -la | grep txt", "instructions": "Pipe the output of ls -la into grep to filter for lines containing 'txt'."}],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which operator appends output to a file instead of overwriting it?',
                                'answer_hash': '0f02c6bad08d9ff1858d26cf1af766e336d71e34c2e74e8c7d417b3550cbfc44',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': "Which character connects one command's output directly into another command's input?",
                                'answer_hash': 'cbe5cfdf7c2118a9c3d78ef1d684f3afa089201352886449a06a6511cfef74a7',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 6,
                        'title': 'Viewing Parts of Files — head, tail',
                        'blocks': [{"type": "text", "heading": "head \u2014 Show the Beginning", "body": "head file.txt prints the first 10 lines of a file by default. This is ideal for quickly checking a large file's format or headers without dumping the entire thing."}, {"type": "text", "heading": "tail \u2014 Show the End", "body": "tail file.txt prints the last 10 lines. This is especially useful for logs, where the most recent (and usually most relevant) entries are at the bottom of the file."}, {"type": "text", "heading": "Controlling the Line Count", "body": "Both commands accept -n to change how many lines are shown: head -n 20 file.txt shows the first 20 lines, tail -n 5 file.txt shows the last 5."}, {"type": "text", "heading": "Following a File Live \u2014 tail -f", "body": "tail -f file.txt doesn't exit after printing \u2014 it keeps watching the file and prints new lines as they're appended, live. This is the standard way to watch a log file update in real time while a server is running."}, {"type": "text", "heading": "Combining with Pipes", "body": "head and tail work naturally in pipelines: ps aux | head -5 shows just the first five running processes from a potentially long list."}, {"type": "practice", "command": "tail -n 5 /var/log/dpkg.log", "instructions": "View the last five lines of a system log file (if present) using tail."}],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': "Which tail flag makes it continuously watch a file and print new lines as they're added?",
                                'answer_hash': '0e6503c1ece40e4ea7668463248ea2716eb37643f2c2c605f8bcee4d195a1705',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 7,
                        'title': 'Sorting & Counting — sort, wc, uniq',
                        'blocks': [{"type": "text", "heading": "sort \u2014 Order Lines", "body": "sort reads lines of input and prints them back in sorted order, alphabetically by default. sort file.txt sorts a file's lines; it's extremely common in pipelines to prepare data for uniq, which requires sorted input to work correctly."}, {"type": "text", "heading": "Numeric and Reverse Sorting", "body": "sort -n sorts numerically instead of alphabetically (important, since alphabetical sort would put '10' before '9'). sort -r reverses the order. sort -rn combines both for largest-to-smallest numeric sort."}, {"type": "text", "heading": "wc \u2014 Word Count", "body": "wc counts lines, words, and characters in its input. wc -l file.txt prints just the line count \u2014 a very common pattern for quickly checking how many entries something has, e.g. cat users.txt | wc -l."}, {"type": "text", "heading": "uniq \u2014 Remove Duplicate Lines", "body": "uniq removes consecutive duplicate lines from its input. Critically, it only catches duplicates that are directly adjacent \u2014 which is why input is almost always piped through sort first: sort file.txt | uniq."}, {"type": "text", "heading": "Counting Occurrences with uniq -c", "body": "uniq -c prefixes each unique line with how many times it appeared consecutively. Combined with sort, sort file.txt | uniq -c | sort -rn gives you a frequency count of every unique line, ordered from most to least common \u2014 an extremely common log-analysis pattern."}, {"type": "practice", "command": "cat /etc/passwd | wc -l", "instructions": "Count how many lines (user entries) are in /etc/passwd."}],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which wc flag prints only the line count?',
                                'answer_hash': '8d29a0f35918ca625667b2858e1c366e227ecbb424c5b30d008a1b2ec709e6d2',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Why must input usually be sorted before piping into uniq?',
                                'answer_hash': '21f274d51d7419c6fe8518b81ddb4b4514b6f816e2830766e9236e9a16120841',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 8,
                        'title': 'Processes — ps, top, kill',
                        'blocks': [{"type": "text", "heading": "What is a Process?", "body": "A process is a running instance of a program. Every process has a unique Process ID (PID), assigned by the kernel, which is used to identify and control it."}, {"type": "text", "heading": "ps \u2014 Snapshot of Running Processes", "body": "ps shows a snapshot of currently running processes. ps aux is the most common invocation: it shows every process on the system (a = all users, u = user-friendly format, x = include processes without a controlling terminal), including PID, CPU%, memory%, and the command that started it."}, {"type": "text", "heading": "top \u2014 Live Process Monitor", "body": "top shows a continuously updating, live view of running processes, sorted by resource usage by default. It's the standard first tool to check when a system feels slow \u2014 it immediately shows what's consuming CPU or memory. Press q to quit."}, {"type": "text", "heading": "kill \u2014 Terminate a Process", "body": "kill <PID> sends a termination signal to a specific process by its PID. By default this sends SIGTERM, a polite request to shut down. kill -9 <PID> sends SIGKILL, an immediate, forceful termination that the process cannot ignore or clean up after \u2014 a last resort when a process is unresponsive."}, {"type": "text", "heading": "Finding a PID to Kill", "body": "A very common pattern combines ps and grep to find a specific process's PID: ps aux | grep nginx shows any nginx-related processes along with their PIDs, which you can then pass to kill."}, {"type": "text", "heading": "pkill \u2014 Kill by Name", "body": "pkill nginx skips the manual PID lookup entirely and kills any process whose name matches 'nginx' directly. It's more convenient but less precise \u2014 worth double-checking the pattern won't match more than you intend."}, {"type": "practice", "command": "ps aux | head -10", "instructions": "List running processes and view the first 10 entries."}],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'What signal number does kill -9 send, which cannot be ignored by the target process?',
                                'answer_hash': '19581e27de7ced00ff1ce50b2047e7a567c76b1cbaebabe5ef03f7c3017bb5b7',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 9,
                        'title': 'Archives & Compression — tar, gzip',
                        'blocks': [{"type": "text", "heading": "tar \u2014 Tape Archive", "body": "tar bundles multiple files and directories into a single archive file, preserving directory structure, permissions, and ownership. Its name is a historical leftover from when archives were written to magnetic tape."}, {"type": "text", "heading": "Creating an Archive", "body": "tar -cvf archive.tar mydir/ creates (c) a new archive, verbosely (v) listing each file as it's added, to the given file (f). This produces an uncompressed .tar file \u2014 just a bundle, not yet compressed."}, {"type": "text", "heading": "Extracting an Archive", "body": "tar -xvf archive.tar extracts (x) the archive's contents into the current directory, verbosely listing each file as it's extracted."}, {"type": "text", "heading": "Compression with gzip", "body": "gzip file compresses a single file in place, replacing it with file.gz. gunzip file.gz reverses the process. gzip alone doesn't bundle multiple files \u2014 that's tar's job."}, {"type": "text", "heading": "Combining tar and gzip", "body": "tar -czvf archive.tar.gz mydir/ combines both in one command \u2014 the z flag tells tar to pipe its output through gzip compression automatically. This is by far the most common way archives are created on Linux, producing the familiar .tar.gz (or .tgz) files. Extraction mirrors this: tar -xzvf archive.tar.gz."}, {"type": "text", "heading": "Checking an Archive's Contents", "body": "tar -tvf archive.tar.gz lists (t) what's inside an archive without actually extracting anything \u2014 useful for checking contents before committing to an extraction."}, {"type": "practice", "command": "mkdir sample && touch sample/a.txt sample/b.txt && tar -czvf sample.tar.gz sample/", "instructions": "Create a small directory with files, then compress it into a .tar.gz archive."}],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which tar flag tells it to compress its output using gzip?',
                                'answer_hash': '594e519ae499312b29433b7dd8a97ff068defcba9755b6d5d00e84c524d67b06',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which tar flag creates a new archive (as opposed to extracting one)?',
                                'answer_hash': '2e7d2c03a9507ae265ecf5b5356885a53393a2029d241394997265a1a25aefc6',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 10,
                        'title': 'Remote Access Basics — ssh, scp',
                        'blocks': [{"type": "text", "heading": "ssh \u2014 Secure Shell", "body": "ssh lets you log into a remote machine over an encrypted connection and get an interactive shell on it, as if you were sitting at its terminal. It's the standard way to administer Linux servers remotely."}, {"type": "text", "heading": "Basic Syntax", "body": "ssh username@hostname connects to 'hostname' as 'username', prompting for a password (or using a key, covered next). ssh username@hostname -p 2222 connects on a non-default port if the server isn't listening on the standard port 22."}, {"type": "text", "heading": "SSH Keys Instead of Passwords", "body": "Rather than typing a password every time, SSH supports public-key authentication: you generate a key pair (ssh-keygen), keep the private key secret on your machine, and place the public key on the server (~/.ssh/authorized_keys). This is both more convenient and more secure than passwords \u2014 the private key never has to travel over the network."}, {"type": "text", "heading": "scp \u2014 Secure Copy", "body": "scp copies files between machines over the same encrypted SSH connection. scp localfile.txt user@host:/remote/path/ uploads a file to a remote server; scp user@host:/remote/file.txt . downloads a file from a remote server to your current directory."}, {"type": "text", "heading": "Why SSH Matters for Security", "body": "SSH replaced older, insecure remote-access protocols like telnet and rsh, which sent everything \u2014 including passwords \u2014 in plaintext over the network. Anyone who understands SSH's basics understands a core piece of how nearly all Linux server administration happens safely today."}, {"type": "practice", "command": "ssh --help", "instructions": "View the ssh command's help output to see its available options (an actual remote connection isn't needed for this lesson)."}],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'What command generates a new SSH key pair?',
                                'answer_hash': 'a24f7bf3c615ad233a251863a4ed0db7f5f286205ea837daddc21bdcce35b907',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'What is the standard default port that SSH servers listen on?',
                                'answer_hash': '785f3ec7eb32f30b90cd0fcf3657d388b5ff4297f2f9716ff66e9b69c05ddd09',
                                'setup_script': None,
                            },
                        ],
                    },
                ],
            },
            {
                'order_index': 3,
                'title': 'Advanced',
                'description': 'Users, scheduling, services, and networking basics.',
                'lessons': [
                    {
                        'order_index': 1,
                        'title': 'Processes in Depth — ps, top, signals',
                        'blocks': [{"type": "text", "heading": "What a Process Actually Is", "body": "A process is a running instance of a program \u2014 the program itself is just bytes on disk; when the kernel loads it into memory and starts executing it, that becomes a process. Every process is assigned a unique Process ID (PID) by the kernel at the moment it starts, and that PID is how you refer to it for the rest of its life. The PID is never reused while the process is alive, and after a process ends, its PID may be recycled by a later process."}, {"type": "text", "heading": "Parent and Child Processes", "body": "Every process (except the very first one, PID 1, usually systemd or init) has a parent process. When you run a command in your shell, the shell forks itself, creating a copy, and that copy execs the program you asked for. The PPID (parent process ID) column in process listings tells you which process launched which. Process trees matter because killing a parent often kills its children \u2014 or, conversely, if a parent dies without reaping its children, they become 'orphans' and get reparented to PID 1."}, {"type": "text", "heading": "Process States", "body": "Every process is in one of a handful of states at any moment. R means running or runnable (either on CPU right now or waiting its turn). S means interruptible sleep \u2014 waiting for something, and can be woken by a signal. D means uninterruptible sleep, usually waiting on disk I/O, and cannot be killed even by SIGKILL until the I/O completes. Z means zombie \u2014 the process has exited but its parent hasn't read its exit status yet. T means stopped, usually because you pressed Ctrl+Z."}, {"type": "text", "heading": "ps aux \u2014 Snapshot of Everything", "body": "ps aux shows every process on the system in a single snapshot. The columns are: USER (who owns it), PID, %CPU, %MEM, VSZ (virtual memory size), RSS (resident memory, the actual RAM in use), TTY, STAT (state), START (when it started), TIME (cumulative CPU time used), and COMMAND. The 'a' means show processes from all users, 'u' means user-oriented format, 'x' means include processes not attached to a terminal. This combination is what you want 95% of the time."}, {"type": "text", "heading": "top and htop \u2014 Live Views", "body": "top shows the same information as ps but refreshing continuously, sorted by CPU by default. The header shows load average (system load over 1, 5, and 15 minutes), total and free memory, and swap usage. Inside top, press M to sort by memory, P to sort by CPU, k to kill a process by PID, and q to quit. htop is a nicer-looking replacement, but it's not always installed. Learning top properly is worth it because it's on every Linux system you'll ever touch."}, {"type": "text", "heading": "Signals \u2014 How You Talk to Processes", "body": "A signal is a small message the kernel delivers to a process, usually to tell it to do something. The most common signals: SIGTERM (15) is a polite request to shut down \u2014 the process can catch it and clean up before exiting. SIGKILL (9) is a forced kill \u2014 the process cannot catch it, cannot clean up, cannot do anything except die. SIGHUP (1) originally meant 'the terminal hung up' and is often repurposed to mean 'reload your config'. SIGINT (2) is what Ctrl+C sends. SIGSTOP and SIGCONT pause and resume a process without killing it."}, {"type": "text", "heading": "kill, killall, and pkill", "body": "kill <PID> sends SIGTERM by default. kill -9 <PID> sends SIGKILL. The PID is required because kill takes a numeric target \u2014 but pkill and killall let you kill by name: pkill nginx kills any process whose name matches nginx, and killall nginx does the same. pkill -f matches against the full command line, which is useful when the process name is generic (like 'python'). Be careful with these \u2014 a loose pattern can kill more than you meant."}, {"type": "text", "heading": "Why 'kill' Is a Misnomer", "body": "Despite its name, kill doesn't necessarily terminate a process \u2014 it just sends a signal. If you send SIGHUP to a daemon, it might reload its configuration and keep running. If you send SIGUSR1 to some programs, they do application-specific things. The default signal (SIGTERM) does mean 'please exit', which is why the command got its name, but thinking of kill as 'send signal N' rather than 'destroy process' is the correct mental model."}, {"type": "practice", "command": "ps aux | head -15", "instructions": "Look at the first 15 processes. Identify the columns, and find your own shell process (the one running your current session)."}, {"type": "practice", "command": "sleep 300 & jobs", "instructions": "Start a long-running command in the background, then list your background jobs. Note the job number and PID."}],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'What does PID stand for?',
                                'answer_hash': 'e94742b317f20b2b4290fe0295e6e346f02552199c2621f87736a6c16223e727|b70e447efa6bc2c12527e4730537c4bd2cd6b7ec7e2b9951aad6ac9c8f2cc719',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'What is the PID of the very first process started on a Linux system (usually systemd or init)?',
                                'answer_hash': '6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which signal number, sent with kill -N, cannot be caught or ignored by a process?',
                                'answer_hash': '19581e27de7ced00ff1ce50b2047e7a567c76b1cbaebabe5ef03f7c3017bb5b7',
                                'setup_script': None,
                            },
                            {
                                'order_index': 4,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which signal does the terminal send when you press Ctrl+C?',
                                'answer_hash': 'ad7ae82daa8d99999cd9babe2efb1e5fa2f9c1c7222005c5024bab413a52dc06|84cbede1b1cbf33dc6a3c4a71eab6d817fcaf810338ec7c0d3969c1f77c252c5|d4735e3a265e16eee03f59718b9b5d03019c07d8b6c51f90da3a666eec13ab35|1713c80cda27c2597419797c0a604b7c0d0b981fc3a254f2fd7624a7efccfef7|6da88c34ba124c41f977db66a4fc5c1a951708d285c81bb0d47c3206f4c27ca8',
                                'setup_script': None,
                            },
                            {
                                'order_index': 5,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'In ps aux output, which column shows the parent process ID?',
                                'answer_hash': 'd4ab95f098ed41b409b0a26b50507ce026f80c07363cc3c4c60397ff94541edc',
                                'setup_script': None,
                            },
                            {
                                'order_index': 6,
                                'question_type': 'text',
                                'difficulty': 'hard',
                                'prompt': "What does a process with state 'Z' mean in ps output, and why can't it be killed?",
                                'answer_hash': '49460b7bbbd3aad3f2cba09864f5e8b01a220ea8c077e9fa996de367e7984af0|e52833d090b11a6343b2c50ca54a780b55e8a8e0e9bc948d8d74b58e5e511cc9|c354077fedad3b2b9fc54b617f469438c289280caa3559aaff01f33ee1b35471',
                                'setup_script': None,
                            },
                            {
                                'order_index': 7,
                                'question_type': 'text',
                                'difficulty': 'hard',
                                'prompt': 'What does the D state mean, and why is it significant compared to other sleep states?',
                                'answer_hash': 'e0e21aeb3b188b2bab6f9ea6f7d98f3849a09a00d2dad383d8d4bac362b0c722|99409672e2f85d985f94e64c6d62c28c7cdb320a1c530851468f46cd2a8c6791',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 2,
                        'title': 'Jobs and Background Processes',
                        'blocks': [{"type": "text", "heading": "Foreground vs Background", "body": "When you run a command in a shell, it normally runs in the foreground: the shell waits for it to finish before giving you back a prompt. Any command that runs longer than a couple of seconds \u2014 a compile, a download, a long-running server \u2014 blocks your shell until it completes, which is inconvenient if you want to keep working. Background jobs solve this by letting the process run while you get your prompt back."}, {"type": "text", "heading": "The & Operator", "body": "Appending & to a command tells the shell to start it in the background. `sleep 300 &` immediately returns you to the prompt while sleep continues running. The shell prints something like [1] 12345 \u2014 the first number is the job number (a shell-local identifier), and the second is the PID (the kernel's identifier). You'll use the job number with shell built-ins and the PID with system-level tools like kill."}, {"type": "text", "heading": "Ctrl+Z, bg, and fg", "body": "If you've already started a foreground process and want it out of the way, press Ctrl+Z. This sends SIGTSTP (stop), pausing the process rather than killing it. You get your prompt back. Now you can type bg to resume it in the background, or fg to bring it back to the foreground. To bring a specific job forward, use fg %2 or bg %2 with the job number. The jobs command lists everything currently paused or running in the background of your shell."}, {"type": "text", "heading": "Why Background Jobs Die When You Log Out", "body": "Background jobs are still children of your shell. When you close the terminal or disconnect SSH, the shell exits, and by default it sends SIGHUP to all its children. For a shell started interactively, huponexit may or may not be set, but SSH sessions typically do send SIGHUP on disconnect. That's why a long-running process you started with & often dies when you log out \u2014 not because anything killed it, but because its parent shell went away and took it with it."}, {"type": "text", "heading": "nohup and disown", "body": "nohup command & runs a command immune to SIGHUP \u2014 the process stays alive even after its parent shell exits, and its output is redirected to nohup.out by default if the terminal goes away. disown removes a job from the shell's job table so the shell won't send it SIGHUP on exit; disown -h just marks it to ignore SIGHUP but keeps tracking it. For real production work you'd use systemd or a process supervisor, but for one-off long-running tasks, nohup and disown are the standard tools."}, {"type": "text", "heading": "Reading Job Output", "body": "A background process still writes to your terminal by default. If you're not careful, its output interleaves with whatever you're typing, making a mess. Redirecting output (command > file.log 2>&1 &) is the standard pattern to keep the terminal clean. The 2>&1 part sends stderr (file descriptor 2) to the same place as stdout (file descriptor 1), so both end up in the log."}, {"type": "practice", "command": "sleep 60 &", "instructions": "Start a sleep in the background. Note the [job] PID that gets printed."}, {"type": "practice", "command": "jobs", "instructions": "List your background jobs. You should see the sleep from the previous step."}],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'What character is appended to a command to run it in the background?',
                                'answer_hash': '951dcee3a7a4f3aac67ec76a2ce4469cc76df650f134bf2572bf60a65c982338',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'What key combination pauses a foreground process and returns you to the prompt?',
                                'answer_hash': 'b135663aec34bc7770010b438398815742754e82c00b7888714636b7a1cb978d|b1b5270c791f1025cd7566849908c9fa052a28a5c273c2df18aa8d883dbcce78|ac0b80788bc2e250291a94283b0f238c70476fbac1722c140d4c38a784cb86af',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which shell built-in resumes a paused job in the background?',
                                'answer_hash': '3f14db6ed20043e880a29460790f5f5cec2a7d38c41795e59fdac71789322af2',
                                'setup_script': None,
                            },
                            {
                                'order_index': 4,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which signal is sent to background jobs when the shell exits, causing them to die?',
                                'answer_hash': 'ed5fb133e31b959f9cab6892b656c3f41f6190b498796aab154dc0da12b0fa5b|7e3578ed551203b40d60a7cfd3946b04d86d459590d609950101d69e9828e0e1|76cccdd4b8f5feafd1b4902763d56fe08f5b37f3e1687d41ac71a77d0e1008f2|6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b',
                                'setup_script': None,
                            },
                            {
                                'order_index': 5,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'What does nohup do to a command?',
                                'answer_hash': 'a57f7d1e9ecae5cba36442d0e4aa6906cc4cda2edbf1445a09155daf8c64c0d7|dfb1ee951f3be34a8704468f68eb5fbb1826af29b5a6ddd1807f37c1b2e15f53|b78d46b6c64181b1d862c07552491f795fe5cc8b0519b12f5d79b9358cb44733',
                                'setup_script': None,
                            },
                            {
                                'order_index': 6,
                                'question_type': 'text',
                                'difficulty': 'hard',
                                'prompt': 'In the shell line `cmd > file.log 2>&1 &`, what does `2>&1` accomplish?',
                                'answer_hash': '7e764a3e466db2f95b17a10440bd616bb8d69656143bd480f94cc0c5f2573051|08735f0391654779bf93e2cd90441c9ce2e11a4f8e7e1e06e897f518a6c044dd|e6fc5b835e2242903410017f7e00edd56fb8a1693f1a8b92eb97be187b8d04a5',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 3,
                        'title': 'Services and systemd',
                        'blocks': [{"type": "text", "heading": "What a Service Is", "body": "A service (also called a daemon) is a long-running process that provides a capability to the system or to other programs. SSH is a service. PostgreSQL is a service. Nginx is a service. They start when the system boots, keep running in the background, and are managed as units rather than as individual processes. Historically, each distribution had its own init system \u2014 SysV init, Upstart, OpenRC \u2014 but today nearly everything uses systemd."}, {"type": "text", "heading": "systemctl \u2014 The Control Command", "body": "systemctl is the command you use to interact with systemd. Every service is referred to by its unit name, usually ending in .service: sshd.service, postgresql.service, nginx.service. You can usually omit the .service suffix \u2014 systemctl start sshd and systemctl start sshd.service are the same thing. systemctl is the modern equivalent of the old service and update-rc.d commands, and both still exist as wrappers on most systems."}, {"type": "text", "heading": "The Core Verbs", "body": "systemctl status <unit> shows whether the unit is running, its PID, recent log lines, and whether it's enabled at boot. systemctl start <unit> starts it now. systemctl stop <unit> stops it now. systemctl restart <unit> stops and starts it. systemctl reload <unit> asks the service to reload its config without restarting (not all services support this). systemctl enable <unit> makes it start automatically on boot. systemctl disable <unit> removes that auto-start. A service can be running but disabled (started manually) or enabled but stopped (will start on next boot), so status output always shows both."}, {"type": "text", "heading": "Unit Files", "body": "Every systemd unit is defined in a text file, usually under /etc/systemd/system/ (custom units) or /lib/systemd/system/ (package-installed units). A unit file has sections like [Unit] (description, dependencies), [Service] (ExecStart, Restart, User), and [Install] (when to enable). The ExecStart line tells systemd what command to run. The Restart= directive tells systemd whether to restart the service if it crashes. Custom services you write yourself go in /etc/systemd/system/ and require systemctl daemon-reload before systemd notices them."}, {"type": "text", "heading": "journalctl \u2014 Reading Service Logs", "body": "systemd captures everything services print to stdout/stderr and stores it in the journal. journalctl -u sshd shows all logs from sshd. journalctl -u sshd -f follows the log live, like tail -f. journalctl -u sshd --since '10 minutes ago' shows recent entries. journalctl -p err shows only error-level messages. This is the modern replacement for digging through /var/log/syslog, and it's what you'll use to debug why a service won't start."}, {"type": "text", "heading": "Why systemd Replaced Init Scripts", "body": "The old SysV init system started services sequentially in a fixed order, based on numbered symlinks in /etc/rc*.d/. It worked, but it was slow and parallel startup was impossible. systemd starts services in parallel using explicit dependencies, tracks which processes belong to which service (via cgroups), can restart failed services automatically, and provides a unified logging system. The tradeoff is complexity \u2014 systemd is a large, opinionated system that some people dislike \u2014 but it's what's running on essentially every modern Linux."}, {"type": "practice", "command": "systemctl status ssh --no-pager 2>/dev/null || systemctl status sshd --no-pager", "instructions": "Check the status of the SSH service. Note whether it says 'active (running)' and whether it's enabled."}, {"type": "practice", "command": "journalctl -u ssh -n 20 --no-pager 2>/dev/null || journalctl -u sshd -n 20 --no-pager", "instructions": "View the last 20 log entries from the SSH service."}],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'What command is used to control systemd services?',
                                'answer_hash': 'ff4b294dcb57179cad146355dcfdca5fb7f516963b73f25f09171ec6d2fb0954',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'What verb makes a service start automatically on boot?',
                                'answer_hash': 'e97166b54500da3a32eae48afe8df0970b19abfde3e4f3a50206cd8509feb161',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which systemctl verb shows whether a service is currently running?',
                                'answer_hash': '073c1634c496cdb649d1afe0a312bbb4b7e1741b271542e4a436c3b8824b1761',
                                'setup_script': None,
                            },
                            {
                                'order_index': 4,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which command reads logs from the systemd journal, filtered by unit with -u?',
                                'answer_hash': '394b7b1486f6bbce37a26c928cee8ceab84df2db9aa7dd538195e4e51494f3bb|37ebafac1092017dd13c204164792ac7351fdc37f798d38bb8fd02d48b81a7a9',
                                'setup_script': None,
                            },
                            {
                                'order_index': 5,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Where do custom systemd unit files usually live on the filesystem?',
                                'answer_hash': '822eaa5daa513a88fa268a3a9b4cb4cd8631d9579865ab093c942e97cb81dfff|70ad7c4c9f2ed024973653d6aaaa7094e510622e08da0f84b5cbf3e840ebe076',
                                'setup_script': None,
                            },
                            {
                                'order_index': 6,
                                'question_type': 'text',
                                'difficulty': 'hard',
                                'prompt': 'After creating or editing a unit file in /etc/systemd/system/, which command must you run for systemd to notice the change?',
                                'answer_hash': '46979156d9adffee389f2a76b4c0b87f3ca07a919675854e675add20b83ced07|abb60b2783ce3ea3d11680ad761b443dc090affaa44fb1e28f8eb14f82c4a69f',
                                'setup_script': None,
                            },
                            {
                                'order_index': 7,
                                'question_type': 'text',
                                'difficulty': 'hard',
                                'prompt': 'What is the difference between `systemctl restart` and `systemctl reload`?',
                                'answer_hash': '86c5ab2f4d686bd52d359f4fb90f74b09633c9c8daa2c4f9cd7a322a2eae09e3|74ea7eeb9315198607ac2464caff6458caae60bab5a0be17ebef51447464d676',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 4,
                        'title': 'Environment and PATH',
                        'blocks': [{"type": "text", "heading": "What Environment Variables Are", "body": "Every process on Linux has an environment: a list of key-value pairs passed to it when it starts. These variables configure how the process behaves without requiring command-line arguments. PATH tells the shell where to look for programs. HOME tells programs where the user's home directory is. USER gives the current username. LANG sets the locale. TERM tells programs what kind of terminal they're talking to. Some are set by the login system, some by your shell config, some by you."}, {"type": "text", "heading": "Reading and Setting Variables", "body": "`echo $HOME` prints a variable's value. `env` or `printenv` lists all current variables. `export FOO=bar` sets FOO and makes it visible to child processes. Without export, a variable is shell-local \u2014 it exists in your current shell but won't be inherited by anything you run. This distinction is the source of one of the most common beginner mistakes: setting a variable, then finding that a program you launched doesn't see it."}, {"type": "text", "heading": "PATH \u2014 How the Shell Finds Commands", "body": "When you type `ls`, the shell doesn't guess \u2014 it walks through each directory in PATH, in order, looking for an executable file named ls. The first match wins. `echo $PATH` shows the directories, separated by colons. Typical value: /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin. If you write your own script and want to run it by name from anywhere, you either put it in a directory already on PATH (usually /usr/local/bin) or add its directory to PATH yourself."}, {"type": "text", "heading": "Prepending vs Appending to PATH", "body": "When adding a directory to PATH, order matters because the first match wins. `export PATH=/opt/mybin:$PATH` prepends \u2014 your directory is searched before the system directories, so your versions of programs shadow the system ones. `export PATH=$PATH:/opt/mybin` appends \u2014 the system takes priority and yours is only used if nothing else matches. Choose deliberately: shadowing system tools is powerful but can break things subtly."}, {"type": "text", "heading": ".bashrc vs .profile vs .bash_profile", "body": "Shell config files control which variables and aliases get set and when. .bashrc runs for every interactive non-login shell \u2014 every new terminal window, in a graphical session. .profile (or .bash_profile for bash) runs once at login \u2014 when you log in via SSH or a console, but not when you open a new terminal tab. The split exists so that slow one-time setup (like loading SSH keys into an agent) only happens at login, while cheap things (aliases, prompt customization) happen in every shell. In practice, many systems have .bashrc sourced from .profile to unify things."}, {"type": "text", "heading": "Sourcing vs Executing", "body": "Running `./script.sh` executes the script in a new shell process \u2014 variables it sets disappear when it exits. Running `source script.sh` (or `. script.sh`) executes it in your current shell \u2014 variables and aliases it sets persist. That's why .bashrc is sourced, not executed, and why after editing .bashrc you run `source ~/.bashrc` rather than `~/.bashrc`. The distinction catches everyone at least once."}, {"type": "practice", "command": "echo $PATH", "instructions": "Print your current PATH. Count how many directories it contains."}, {"type": "practice", "command": "env | head -20", "instructions": "List the first 20 environment variables. Note which ones look familiar."}],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'What command prints the value of an environment variable named FOO?',
                                'answer_hash': '6358a51b47d154297d6e49c70469b3bfbd4baa420b9f80625ab104b65b0b441a|6358a51b47d154297d6e49c70469b3bfbd4baa420b9f80625ab104b65b0b441a|17e0cf832ec1476245d59735abf2e9b73c4f7e4e453bfba3d13bf87a7d841842|17e0cf832ec1476245d59735abf2e9b73c4f7e4e453bfba3d13bf87a7d841842',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which shell keyword makes a variable visible to child processes?',
                                'answer_hash': 'd46aee08cc49f6d1eb41800c1d6bab4506c960c700cff0efffe490d7cb1de5e3',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'What character separates directories in the PATH variable?',
                                'answer_hash': 'e7ac0786668e0ff0f02b62bd04f45ff636fd82db63b1104601c975dc005f3a67',
                                'setup_script': None,
                            },
                            {
                                'order_index': 4,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which file is typically sourced on every interactive shell launch, making it the right place for aliases?',
                                'answer_hash': 'b7cf3e96e1f74fc148d130e98db1c65c7b8eb4f5b668668fa71f26768796a5b0|0da5c317b06e27c114cfe2d03f364697eb07cc21e19a9c71b75c9152528bb24f|47e4d9c40c4c556785013534c987df9eeaed40029d4c90ebe00058c864de953f',
                                'setup_script': None,
                            },
                            {
                                'order_index': 5,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'When multiple directories in PATH contain a program with the same name, which one runs?',
                                'answer_hash': '4df652a21271503eb53eab9b7c1fe8d14f48b689ba67ad90680fdb1eda0a5be6|592704afb51bbc6de366836c3bbb367b9b0b86aa8e3a72676d7498f712d72823|ada8836c09565bc9cbb60998233c7500c09d83f5c6e5315d63c8e98b34bcf64a',
                                'setup_script': None,
                            },
                            {
                                'order_index': 6,
                                'question_type': 'text',
                                'difficulty': 'hard',
                                'prompt': 'What is the difference between running a script with `./script.sh` and `source script.sh`?',
                                'answer_hash': '922af232f34e996cb38b1c86cdf311ac770799e24a9d48da60ccc465f1057bc3|1169cc35f4669e348d54a6bb10177dd32ec266475ab1ae574dc24f766ed74b45',
                                'setup_script': None,
                            },
                            {
                                'order_index': 7,
                                'question_type': 'text',
                                'difficulty': 'hard',
                                'prompt': 'Why might .profile and .bashrc both exist rather than just one file?',
                                'answer_hash': 'f8b88e51f78af79e4a301c8a1cd3cc3b32fa6d8498ad16575bac943990574bd8|20ffd233144665982a5f85771be021ee000cd9bcc34071a6bc1084a08b89d5c2|debe66462949d231dd17830d3e3907c48ddfe2e7ea8b3954f0db4006d162544b',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 5,
                        'title': 'Users, Groups, and Identity',
                        'blocks': [{"type": "text", "heading": "Why Linux Is Multi-User by Design", "body": "Linux was built as a time-sharing system: many users logged into the same machine simultaneously, each with their own files, processes, and permissions. That architecture hasn't changed. Even a single-user laptop treats every file and process as belonging to a specific user. When you add a service like nginx, it runs as its own user. When you install a database, it gets its own user. Understanding how users and groups work isn't academic \u2014 it's how you reason about who can do what on a system."}, {"type": "text", "heading": "The User Database \u2014 /etc/passwd", "body": "/etc/passwd is a plain text file listing every user account on the system. Each line has seven colon-separated fields: username, password placeholder (historically the hashed password, now usually just 'x'), UID (numeric user ID), GID (primary group ID), GECOS (full name or comment), home directory, and login shell. Even though it's called 'passwd', the actual password hashes live in /etc/shadow, readable only by root \u2014 that separation exists so that non-root programs can read usernames and IDs but not password hashes."}, {"type": "text", "heading": "UIDs and the Root Account", "body": "Every user has a numeric UID. UID 0 is special \u2014 it's root, the superuser, with no permission restrictions. UIDs 1\u2013999 are typically reserved for system accounts (daemons and services), and UIDs 1000+ are for regular human users. The kernel doesn't care about usernames \u2014 it compares UIDs for permission checks. When you 'become root' with sudo, your effective UID becomes 0 for that command. The username-to-UID mapping is just a human convenience."}, {"type": "text", "heading": "Groups \u2014 Sharing Made Simple", "body": "A group is a named collection of users. Every file has one owner and one group. When a file has group permissions (rwx for group), any user who is a member of the file's group gets those permissions. This is how you share access without giving everyone their own copy: put users in a group, chgrp the file to that group, chmod g+rw the file, done. Every user has a primary group (the GID in /etc/passwd) and can belong to any number of supplementary groups (listed in /etc/group)."}, {"type": "text", "heading": "Managing Users \u2014 useradd, usermod, userdel", "body": "useradd -m -s /bin/bash alice creates a new user 'alice' with a home directory (-m) and bash as their shell (-s /bin/bash). usermod -aG sudo alice adds alice to the sudo group \u2014 the -a is critical, without it usermod replaces all existing groups with just sudo. passwd alice sets or changes alice's password. userdel -r alice deletes the user and their home directory. Every one of these commands modifies /etc/passwd, /etc/shadow, or /etc/group under the hood \u2014 you can edit those files directly in a pinch, but the tools handle locking and validation correctly."}, {"type": "text", "heading": "The id Command", "body": "id with no arguments shows your own UID, primary GID, and all supplementary groups. id alice shows the same for another user. id -u prints just the UID, id -g just the primary GID. This is the definitive way to answer 'what groups am I actually in?' \u2014 more reliable than trying to remember what you added yourself to and when. It's especially useful after adding yourself to a group, when you need to verify the change took effect (it usually requires a new login or `newgrp` to pick up)."}, {"type": "practice", "command": "id", "instructions": "Show your own UID, GID, and group memberships."}, {"type": "practice", "command": "cat /etc/passwd | tail -5", "instructions": "Look at the last 5 lines of the passwd file. Identify the seven colon-separated fields."}],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'What numeric UID does the root user have?',
                                'answer_hash': '5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which file lists all user accounts on the system?',
                                'answer_hash': '74acf31844532670be412c65b8251ee55d072549080b1cffdbea6b1a192230a0|af896a5f354b5297fb7dde9efe8f2b1de11e2fc5315fe28ce1d7468c1953b7ab',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which file stores the actual password hashes, readable only by root?',
                                'answer_hash': '7b5ddf499844cf05866927513cf62fee9af8c281812def040b964146b0ea87d6|fc27ccfa93f112c61779d5d8e15c2a47633c1a27a17cc66b5021e490d76d347a',
                                'setup_script': None,
                            },
                            {
                                'order_index': 4,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'What command adds an existing user to a supplementary group without removing them from their current groups?',
                                'answer_hash': '5cbb0648d6642c1af8345222e1866d87b2d657b2bb083b2f65209333364210ae|a1083e2e275925d71e3aa0f642e8f201b2900d377f0843d7346d26db9efd7e51|5cbb0648d6642c1af8345222e1866d87b2d657b2bb083b2f65209333364210ae',
                                'setup_script': None,
                            },
                            {
                                'order_index': 5,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'What does the -m flag do when passed to useradd?',
                                'answer_hash': '247f50cded20224bf3ce91b7799b2fb310d7fda414ca351fcb6bca7e472b4975|6538195dee377b23601065ab68f955b755f9970aa4a018372ab3188748a1a060',
                                'setup_script': None,
                            },
                            {
                                'order_index': 6,
                                'question_type': 'text',
                                'difficulty': 'hard',
                                'prompt': 'Why does /etc/passwd not contain password hashes, even though its name suggests it should?',
                                'answer_hash': '8fc6de0e1eb0e52938ad4d0a44f611ca1e6d453bef4ebf858824f941a9b370cb|78ce2c246d17438537a74200963dd4c147aa7f6a16cd47b3a391d729d7de5a18',
                                'setup_script': None,
                            },
                            {
                                'order_index': 7,
                                'question_type': 'text',
                                'difficulty': 'hard',
                                'prompt': "If you run `usermod -G developers alice` (without -a), what happens to alice's other supplementary groups?",
                                'answer_hash': '1b51124cd1a473fb17bdb2f7410c2e1f0683803b851fea56b72c7c7fe4a6713a|67982197b054641ec320b88e88603c5f5f477854b2e0c23617ec4bc7ade5020f|85c601af92c1036eee1dd962a541e53d734eefd5136f176c464f9e212414cb98',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 6,
                        'title': 'Sudo Deep Dive',
                        'blocks': [{"type": "text", "heading": "What sudo Actually Does", "body": "sudo runs a single command as another user (by default, root) without requiring you to log in as that user. The command runs in a new process, with an effective UID of root (or whichever user you specify). When the process exits, you're back to being yourself. sudo is not a privilege escalation tool in the malicious sense \u2014 it's an audited, configurable, per-command delegation mechanism that lets administrators grant specific powers to specific users without giving away the root password."}, {"type": "text", "heading": "How sudo Authenticates You", "body": "When you run sudo, it asks for YOUR password, not root's. That's intentional: the system is verifying 'is this really alice, the user we authorized?' not 'does this person know the root password?' After a successful authentication, sudo caches the credential for a few minutes (default 15) so you don't retype it every time. `sudo -k` clears the cache immediately. `sudo -v` refreshes it without running a command \u2014 useful before starting a long sequence of sudo commands."}, {"type": "text", "heading": "The /etc/sudoers File", "body": "Sudo rules live in /etc/sudoers, edited only through the visudo command \u2014 never with a regular text editor, because visudo validates the file before saving and refuses to write syntactically broken rules that would lock you out. A typical rule looks like `alice ALL=(ALL:ALL) ALL`, meaning: user alice, on any host, may run any command as any user and any group. The first ALL is the host, the second is (target_user:target_group), the third is the commands allowed. Reading it out loud helps: 'alice anywhere may run anything as anyone.'"}, {"type": "text", "heading": "The /etc/sudoers.d/ Drop-In Directory", "body": "Rather than editing /etc/sudoers directly, modern practice is to add small files under /etc/sudoers.d/. Each file follows the same syntax as sudoers itself. This avoids merge conflicts when packages update the main file and makes it easy to remove a single rule by deleting a file. The main /etc/sudoers usually has a line `#includedir /etc/sudoers.d` (with a # at the start \u2014 that's intentional, not a comment; sudo's syntax uses #includedir as a directive). You can still create and edit these files only via visudo: `visudo -f /etc/sudoers.d/myrule`."}, {"type": "text", "heading": "NOPASSWD and Other Options", "body": "Some deployments allow passwordless sudo for specific commands \u2014 common for automation, but a security tradeoff since anyone who compromises the user can run those commands without further credentials. The syntax is `alice ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart nginx`. Restricting to specific commands is much safer than blanket NOPASSWD. Other useful directives: Defaults timestamp_timeout=0 disables credential caching, Defaults env_reset strips environment variables from the sudo'd process, and Defaults secure_path overrides PATH during sudo to a safe default."}, {"type": "text", "heading": "sudo -u and sudo -i", "body": "sudo -u postgres psql runs psql as the postgres user instead of root. This is how you access databases whose admin accounts aren't meant to be logged into directly. sudo -i starts a full interactive login shell as root \u2014 you get root's environment, root's PATH, and root's shell config. sudo -s starts a non-login shell as root, retaining your current environment. sudo su - is equivalent to sudo -i but spawns an extra process. For one-off commands, sudo <command> is the right answer; for extended root work, sudo -i is cleaner than running every command with a sudo prefix."}, {"type": "text", "heading": "Why sudo Beats su", "body": "The classic alternative to sudo is su, which asks for the target user's password and gives you a full shell as that user. sudo is preferred because: (1) it doesn't require sharing the root password, (2) every invocation is logged to /var/log/auth.log with the user, command, and time, (3) it can be restricted per-user and per-command, and (4) it doesn't require a full root shell just to run one command. Modern security standards strongly favor sudo or a comparable privilege-management tool over shared root credentials."}, {"type": "practice", "command": "sudo -l", "instructions": "List the sudo rules that apply to your user. If you have no sudo access, this will fail with a permission error \u2014 that's fine, note it."}, {"type": "practice", "command": "sudo -u postgres whoami", "instructions": "Run whoami as the postgres user. You should see 'postgres' printed if sudo is configured correctly."}],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Whose password does sudo ask for when you run a command?',
                                'answer_hash': 'c46e0d05b76b577ee0d73232d54fab3dfe73416f3ced97c0a7f2b8c90a46a615|98e73ab04fc05e1b003c9bd2f9f97291e52987aabb9f377f2eb273067b64a5f7|5eb2da9c26b65531549c8863fa023f9b48c1d3f0e17e01d7c4978876c724b21f|66ebb3e1ed156a03801ecf5c40320bd8a3720f07d65612c486fd7b65ac268135',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'What command must be used to safely edit /etc/sudoers?',
                                'answer_hash': '8ce43c90047b2eb7dcf4fa3f596eaa25381609d619431b5e69a6188887c52d1b',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'What flag makes sudo run a command as a user other than root?',
                                'answer_hash': '99f14531f2599afdb9ace38c18c10740fd29ca1bdcdb7d0460fd799001d567bd|37b99ae598b110c4ea0f54e7463416ebe67dc69e13b4439335e2e4019dc84d4b',
                                'setup_script': None,
                            },
                            {
                                'order_index': 4,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'In the sudoers rule `alice ALL=(ALL:ALL) ALL`, what does the third ALL represent?',
                                'answer_hash': 'a9c10a48cc57bc1c219a9708049f3e0e1ba28b2817fc8f452460253bd690f21c|10f5f77eef9a6b43dc5bf972c7cfd101133e5b738b5e46a0fcdf9021b13b0519|59489b1cb5f646eba5d4b63e84f37a22bfb266dc29946a1f86c77f4caeef9495',
                                'setup_script': None,
                            },
                            {
                                'order_index': 5,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'What sudo directive lets a user run a specific command without being prompted for a password?',
                                'answer_hash': 'c797f6834c354fedaee9e19bd52583f73ee2255bea1d6cc412168eff78675c99',
                                'setup_script': None,
                            },
                            {
                                'order_index': 6,
                                'question_type': 'text',
                                'difficulty': 'hard',
                                'prompt': 'Why must /etc/sudoers only be edited with visudo, and what happens if you use a plain text editor instead?',
                                'answer_hash': '38481887331d47ec898d3aafc53db96d199c608aec1074e79e1b6cd8ab3958dc|f7c62ed04bb10148379a9af837807125836c7e2233eb58e8a0a09ca2eb1f5e24',
                                'setup_script': None,
                            },
                            {
                                'order_index': 7,
                                'question_type': 'text',
                                'difficulty': 'hard',
                                'prompt': 'What is the difference between `sudo -i` and `sudo -s`?',
                                'answer_hash': 'e61d428d6f88dd411ffbcea4ddfcf694ec1c2240be634b70c346275973781497|fa63382701f39aa4b76c98544c7756aee067a0f7640dd5bedd3586fad652e92f',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 7,
                        'title': 'Bash Scripting I — Variables, Logic, Loops',
                        'blocks': [
                            {"type": "text", "heading": "From Commands to Programs", "body": "Everything you've typed so far has been one command at a time. A script is simply saved commands the shell executes in order — and Bash adds the programming constructs that make saved commands genuinely powerful: variables, decisions, loops, and functions. Chapter two of any Linux career starts here."},
                            {"type": "text", "heading": "Anatomy of a Script", "body": "The first line, #!/bin/bash, is the shebang — it tells the kernel which interpreter to use when the file is executed. Save this as greeting.sh, make it executable with chmod +x greeting.sh (covered in Intermediate), and run it with ./greeting.sh. Bash scripts almost universally use the .sh extension, though the kernel doesn't require it — the shebang does the work."},
                            {"type": "text", "heading": "Variables", "body": "NAME=dave assigns (no spaces around =); $NAME reads it. Everything is a string until math is needed: COUNT=$((COUNT+1)) does arithmetic. Command substitution captures output: FILES=$(ls | wc -l) stores the file count. Curly braces disambiguate boundaries: ${NAME}_backup appends _backup to the value instead of looking up a variable called NAME_backup."},
                            {"type": "text", "heading": "Conditionals", "body": "if [ -f /etc/passwd ]; then echo exists; fi tests a condition between [ ] (spaces are mandatory), with fi closing the block. elif and else chain alternatives. Common file tests: -f file exists, -d directory exists, -z string is empty, -x is executable. Numeric comparisons: -eq, -ne, -lt, -gt. String comparisons use = and !=. The keyword form if [[ ... ]] is more forgiving and modern — prefer it in new scripts."},
                            {"type": "text", "heading": "case — Cleaner Multiway Branching", "body": "case $1 in start) echo starting;; stop) echo stopping;; *) echo usage: $0 start|stop;; esac dispatches on a value — each branch ends with ;; and * is the catch-all. Scripts that take arguments like start/stop/reload are the standard shape of every init script and container entrypoint."},
                            {"type": "text", "heading": "Loops", "body": "for f in *.log; do echo $f; done iterates a list. The C-style for ((i=1; i<=5; i++)) counts. while loops until a condition breaks: while read line; do echo $line; done < input.txt walks a file line by line — one of the most-used patterns in log processing."},
                            {"type": "text", "heading": "Your First Real Script", "body": "Combining everything: check disk space and warn. if [ $(df / | tail -1 | awk '{print $5}' | tr -d '%') -gt 90 ]; then echo 'disk almost full' | mail -s alert admin@x; fi. This is exactly the shape of the disk-usage alert script in this chapter's projects — and of thousands of production scripts."},
                            {"type": "practice", "command": "for i in 1 2 3; do echo loop $i; done", "instructions": "Run a for loop directly on the command line — no script file needed."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': "What is the first line of a Bash script that tells the kernel to use Bash called? (one word)",
                                'answer_hash': 'c8c91095817f0cf3a7bd74e5a0104431cde285d893acbfc3b3d73396ea8844be',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which Bash keyword starts a multiway branch, cleaner than a chain of if/elif? (the keyword itself)',
                                'answer_hash': 'bbfcd4160a1e8674dac62292ae48be4785262ad7078f9ec11b74a254ce70fa06',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which keyword closes an if block in Bash? (two letters)',
                                'answer_hash': 'b4bdc848109722a383d0a972c6eb859f2abd29565b8c4cc7199e7c9eb708f1b7',
                                'setup_script': None,
                            },
                            {
                                'order_index': 4,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which special variable holds the exit status of the last command? (exact syntax)',
                                'answer_hash': '3a7494a25ddba0825f3b329bd0f3c370086396e2ede4204819e1d223f85a2468',
                                'setup_script': None,
                            },
                            {
                                'order_index': 5,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which keyword reads one line of input into a variable, e.g. read line? (the keyword itself)',
                                'answer_hash': '3316348dbadfb7b11c7c2ea235949419e23f9fa898ad2c198f999617912a9925',
                                'setup_script': None,
                            },
                            {
                                'order_index': 6,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which keyword repeats a block over a list, e.g. over all *.log files? (three letters)',
                                'answer_hash': '10c22bcf4c768b515be4e94bcafc71bf3e8fb5f70b2584bcc8c7533217f2e7f9',
                                'setup_script': None,
                            },
                            {
                                'order_index': 7,
                                'question_type': 'terminal',
                                'difficulty': 'medium',
                                'prompt': 'How do you make a script executable for owner, group, and others with one chmod symbolic mode? (e.g. chmod ? file.sh)',
                                'answer_hash': '753e9f854e2c64006dfe68087058f4b58efe4398dbc144b1b41bc81afc3f4948|04a6fb16934512861d5643dc9a5f8e7881cf42630a6f23699a6bca66d01ffbf9',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 8,
                        'title': 'Bash Scripting II — Functions, Errors, Logging',
                        'blocks': [
                            {"type": "text", "heading": "Functions — Structure for Scripts", "body": "A function bundles steps under a name: backup() { tar -czf /backup/home.tar.gz /home; log 'backup done'; } — call it later just by typing backup. Functions turn a 200-line script into a readable main that calls do_backup, do_rotate, do_notify — the difference between a script you can maintain and one you're afraid of."},
                            {"type": "text", "heading": "Exit Codes — The Contract", "body": "Every command ends with an exit status: 0 means success, non-zero means failure, and $? reads it. Your scripts should honor the contract: exit 0 on success, exit 1 on failure. This is what lets cron, systemd, and other scripts react to your script's result — a backup script that always exits 0 is invisible when it breaks."},
                            {"type": "text", "heading": "set -e — Fail Fast", "body": "set -e at the top makes the script abort on the first failing command instead of continuing in a broken state. Production scripts nearly always begin with set -euo pipefail — e (errexit), u (error on unset variables), o pipefail (a pipeline fails if any stage fails). This one line prevents an entire class of silent-partial-failure bugs."},
                            {"type": "text", "heading": "Logging Output", "body": "A script run from cron has no terminal — its output vanishes (the cron lesson covers this). The fix: redirect as you go — echo '[$(date)] starting' >> /var/log/mytask.log — or exec > logfile 2>&1 once at the top to send everything. Structured, dated log lines are how a script explains itself when you weren't watching."},
                            {"type": "text", "heading": "Debugging — set -x", "body": "set -x makes Bash print every command before running it — a built-in trace. Run bash -x script.sh for one-off debugging without editing the file. Together with exit codes, this closes the loop: a script that logs what it did and exits honestly can be trusted, monitored, and scheduled."},
                            {"type": "text", "heading": "The Shape of Real Automation", "body": "The chapter's projects are all this shape: a backup script (tar or rsync + rotation + exit codes, scheduled by cron — covered next in the Master room), an update script (apt update && apt upgrade -y with logging), a disk alert (the conditional above), a user-creation script (useradd in a loop with validation). You now know every building block; the rest is assembly."},
                            {"type": "practice", "command": "echo 'echo hello from a script' > t.sh && bash t.sh && rm t.sh", "instructions": "Create, run, and remove a one-line script — the full edit-run loop in one line."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'What exit status does a command or script return when it succeeds? (just the number)',
                                'answer_hash': '5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which set option aborts the script on the first failing command? (the option letter or its long name)',
                                'answer_hash': '825769eed1c7cd6531f7d329eba635d64140a7ee9d8c6363ff00a953d7e071f9|44d2846e091eb9e7b6ac807e4d426fc83e819cec5681288eb3696a5c0e3d3678|5f2c54cdf58b5cadb0b1fa36700322f94977e7b364096160c3c21821d9a780bb',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which set option prints each command before executing it — a built-in debugger?',
                                'answer_hash': 'a420962426d711880258b007d6767792992f6700fa93f127dafe1f7333e50466|27f93a475dfcd5661e2623121f84667eb4843b1197591a6b974868e1a0b5c21e|3ee3a995ecfb85429c79d972472e8d40e87f7f4ad39ebdebf67c331ead79885b',
                                'setup_script': None,
                            },
                            {
                                'order_index': 4,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which Bash keyword defines a reusable block of commands under a name?',
                                'answer_hash': '78f9ac018e554365069108352dacabb7fbd15246edf19400677e3b54fe24e126|f63827270b16435ec0797b109e4a4a9585602610d5ce21e272839ea66d5994d6',
                                'setup_script': None,
                            },
                            {
                                'order_index': 5,
                                'question_type': 'terminal',
                                'difficulty': 'medium',
                                'prompt': "Give one way to run a script called backup.sh in the current directory (type it as you would in the terminal).",
                                'answer_hash': 'cf8935a021c218668f51529cca8e4b37ebc3e15afb7a4e656ed99b832e3328d2|c02780c7683223380f3905d603d38b71a406661f4286da3aa420cc33fe405e4b|6522897b6e77cae9487a50a3d139416d15d01ec0285e9658fee89173ef318fe4|494696fdf01dc0ecc003720f8fa7897a8e80dba3827aaaaf76ccd92a76ea0dd7|76061167871a15c717061fde1ddc169ccf7f9d236d0368bcc6f57d3329036946|be4bf4ba9ee5fbc90bfad8d83c391e2779297094716a34773623d94774e51316',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 9,
                        'title': 'Finding Things — find, locate, which',
                        'blocks': [{"type": "text", "heading": "The Case for find", "body": "find is the workhorse for locating files and directories on Linux. Unlike tools that search a pre-built index, find walks the filesystem tree in real time, evaluating expressions against every entry it encounters. That makes it slower than an indexed search but always up-to-date and far more powerful: you can search by name, size, modification time, permissions, owner, inode, and combine these with boolean logic. Learning find properly is one of the highest-leverage skills in Linux."}, {"type": "text", "heading": "Basic Syntax", "body": "The form is `find <where> <expression>`. `find /etc` alone lists every entry under /etc. `find . -name '*.conf'` searches the current directory for anything matching the glob *.conf. The dot means 'start here', the -name predicate filters by filename. `find / -type f` lists every regular file on the whole system \u2014 slow, but instructive. `find /var -type d` lists every directory under /var."}, {"type": "text", "heading": "Common Predicates", "body": "-name matches the filename with shell globs. -iname is case-insensitive. -type f/d/l matches regular files, directories, or symlinks. -size +10M matches files larger than 10 megabytes. -mtime -7 matches files modified within the last 7 days. -mmin -60 matches files modified in the last 60 minutes. -user alice matches files owned by alice. -perm 644 matches files with exactly those permissions. You can combine any of these with -a (AND, the default), -o (OR), and ! (NOT)."}, {"type": "text", "heading": "-exec \u2014 Running a Command on Each Match", "body": "find doesn't just list \u2014 it can act. `find /tmp -name '*.log' -exec rm {} \\;` deletes every .log file in /tmp, running rm once per match. The `{}` is a placeholder for the matched file, and `\\;` terminates the -exec clause (the backslash escapes the semicolon so the shell doesn't eat it). For efficiency, use `-exec cmd {} +` instead: this batches many files into a single command invocation, which is dramatically faster for large result sets. `-delete` is a built-in shorthand for deleting matches."}, {"type": "text", "heading": "locate \u2014 Fast but Indexed", "body": "locate filename returns instant results because it searches a pre-built database at /var/lib/mlocate/mlocate.db instead of walking the disk. The database is refreshed periodically by updatedb, usually once a day via cron. The tradeoffs: locate can't see files created since the last update, and it doesn't support predicates like -size or -mtime. For 'I know the name, just find it fast', locate wins. For 'find files matching arbitrary criteria', find wins. If locate returns nothing, try `sudo updatedb` to refresh the index."}, {"type": "text", "heading": "which, whereis, and type", "body": "For locating executables specifically, these three are the tools. `which ls` walks your PATH and prints the full path of the first match \u2014 the actual binary the shell would run. `whereis ls` searches a predefined set of directories (including man pages) and shows all hits. `type ls` is a shell built-in that reveals whether ls is a binary, an alias, a function, or a shell keyword. `type` is the most informative because it knows about shell constructs that `which` and `whereis` can't see."}, {"type": "practice", "command": "find /etc -name '*.conf' -type f | head -10", "instructions": "Find the first 10 configuration files under /etc."}, {"type": "practice", "command": "which bash && type bash", "instructions": "Locate the bash binary and see how the shell classifies it."}],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which command searches the filesystem in real time based on predicates?',
                                'answer_hash': 'e6640de835ad09fb0a7367ee2e0ba99d0142c139db0272146e35538bd07479fc',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'What find predicate restricts matches to regular files only?',
                                'answer_hash': 'f8347f63803b4206159a1f9b1050148f64f161b2ef2b58cdedae00c10aefee73|11368c3d2069e8c46dbc3fb1a305fdb7f4a7a6f083f8a0fc987ea042866ef438|44094b14ccc6f7f6aee306068112f7dc23a3edf25bb483b60c76634181a638ae',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which find flag runs a command on each match, with `{}` as the placeholder for the matched file?',
                                'answer_hash': 'e3d7986d77ad84fc4319facfaf5e33d9aa5c1767722c6b255c6cb8d300e3ba81',
                                'setup_script': None,
                            },
                            {
                                'order_index': 4,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which find predicate matches files modified within the last 7 days?',
                                'answer_hash': '51d811092e684138d9ccdd9788f935dfa7130189b72eea8be4d367cee956dda8|9840ac6dd65c5f1b849cd36addefc00190c8da503b1fdfc17fc71c5a0b3dea4c',
                                'setup_script': None,
                            },
                            {
                                'order_index': 5,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which command searches a pre-built database of filenames instead of walking the disk?',
                                'answer_hash': 'c61d02ef654ab458ca503d92e653f4d9b689028678dc04918424b67660a2358c',
                                'setup_script': None,
                            },
                            {
                                'order_index': 6,
                                'question_type': 'text',
                                'difficulty': 'hard',
                                'prompt': 'What is the difference between `-exec cmd {} \\;` and `-exec cmd {} +`?',
                                'answer_hash': '17b46f7e042131fed96b24eda575f27764b072b529f39ad6ed807a6bb9107043|82817d8d93fae8cc15ec0c33531d2324ecaf49a031279035f1e409f33696ddd8',
                                'setup_script': None,
                            },
                            {
                                'order_index': 7,
                                'question_type': 'text',
                                'difficulty': 'hard',
                                'prompt': 'Why might `which ls` return a different result than `type ls`?',
                                'answer_hash': '68a434bd8c5908ff6e2d72e743af2ed00fe397150baf914b170868ea8a587462|464253c3814da606057309ef8477ed78783117ad1577c8b638dcb75d385c7721',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 10,
                        'title': 'Disk Usage and Mounts',
                        'blocks': [{"type": "text", "heading": "Linux's Single Tree", "body": "Linux presents a single unified filesystem tree, with / at the top. But the underlying storage is rarely a single disk \u2014 it's typically one root partition plus additional filesystems 'mounted' at specific directories. /home might be on a separate disk. /var might be on another. External drives plug in and mount at /media/usb. tmpfs filesystems exist purely in RAM and mount at /tmp or /run. Everything appears in one tree because the kernel hides the separate devices behind mount points."}, {"type": "text", "heading": "df \u2014 Disk Free Space", "body": "`df` reports how much space is used and available on each mounted filesystem. `df -h` gives human-readable sizes (MB/GB instead of raw bytes). The columns are: Filesystem (the device name), Size, Used, Avail, Use% (percentage used), and Mounted on (where in the tree it appears). A common pattern: `df -h /var/log` shows free space on the filesystem containing /var/log, which is what you actually care about when a log directory fills up."}, {"type": "text", "heading": "du \u2014 Directory Usage", "body": "Where df summarizes whole filesystems, du summarizes directories. `du -sh /home` prints a single-line total for /home in human-readable form. `du -sh /home/*` shows a total for each subdirectory \u2014 this is the standard way to find what's eating disk space. `du -h --max-depth=1` from a directory gives a one-level breakdown. du can be slow on large trees because it has to walk every file; df by contrast is instant because the kernel tracks filesystem statistics directly."}, {"type": "text", "heading": "mount and the /etc/fstab File", "body": "`mount` with no arguments lists all currently mounted filesystems. `mount /dev/sdb1 /mnt/usb` mounts a device at a directory. `umount /mnt/usb` (note the missing 'n') unmounts it. Mounts are persistent via /etc/fstab, a config file listing each filesystem, its mount point, filesystem type, mount options, and two numbers (dump and fsck order). The system reads fstab at boot and mounts everything listed. If a device in fstab is missing or has wrong UUID, boot can fail or drop to a recovery shell \u2014 one of the most common production outages."}, {"type": "text", "heading": "lsblk \u2014 Block Devices", "body": "`lsblk` lists all block devices on the system \u2014 physical disks, partitions, LVM volumes, loopback devices \u2014 in a tree layout that shows their relationships. It's the fastest way to see 'what disks exist and where are their partitions mounted?' The output shows device names (sda, sdb, nvme0n1), sizes, types (disk vs part vs lvm vs loop), and mount points. `lsblk -f` adds filesystem type and UUID, which is what you need when filling out fstab entries."}, {"type": "text", "heading": "Why 'No Space Left' Happens With Free Space", "body": "Two common gotchas cause 'no space left on device' errors when df shows plenty of free space. First, if the filesystem is out of inodes \u2014 the fixed pool of file metadata slots \u2014 you can't create new files even with gigabytes free. `df -i` shows inode usage; small-file-heavy workloads (mail spools, node_modules) hit this. Second, deleted files that are still held open by a process don't free their disk space until the process closes them. `lsof +L1` lists deleted-but-open files. Restarting the holding process releases the space."}, {"type": "practice", "command": "df -h", "instructions": "List all mounted filesystems with human-readable sizes. Note the Use% of each."}, {"type": "practice", "command": "du -sh /etc /var /usr 2>/dev/null", "instructions": "Show the total size of three common top-level directories."}],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which command reports free and used space on mounted filesystems?',
                                'answer_hash': '32c220482c68413fbf8290e3b1e49b0a85901cfcd62ab0738760568a2a6e8a57',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which flag makes df output human-readable sizes (MB, GB) instead of raw bytes?',
                                'answer_hash': '05dc0e47773fb3a7a4dc132574919f02b6242879820e347dc00a1962a96636b5|798339512a506f29d1c0b37e9e8cbaec68357873a3b840c9b10379d6632cbae2',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which command summarizes how much disk space a specific directory occupies?',
                                'answer_hash': '601b2c2473811afea7864a21e4b965a970afa4ce9eaf85dbdf01414bca66c12c',
                                'setup_script': None,
                            },
                            {
                                'order_index': 4,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which file lists filesystems to mount automatically at boot?',
                                'answer_hash': 'cf54dfacf32eec1c86e0406e395f1251d4e359a523cf6ea7f5e68d45cf692b59|f8f129f6153c1f329bcfe966cfca6e51800e3b11464edadeb10372973a66db8e|06ee72e7ccf61e9cda8d84478ddf6eae46c31155d0216d12619846060f3acd39',
                                'setup_script': None,
                            },
                            {
                                'order_index': 5,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which command displays all block devices and their mount points in a tree layout?',
                                'answer_hash': 'ade8891466c48206771f3cb0dfc42306b257e1e28b684141f4beb824832922f5',
                                'setup_script': None,
                            },
                            {
                                'order_index': 6,
                                'question_type': 'text',
                                'difficulty': 'hard',
                                'prompt': "You have 10 GB free on a filesystem but 'No space left on device' errors persist. What are the two most likely causes?",
                                'answer_hash': '85331734018e072296a8e9b090008833fd509a492d5689dd9dced3a42253263f|5806b2a201c961b57ad926da3a931362646ae413a6c41b44bcc29b202105c391|7be38428c835d77102e2080433b34df68f44436321fdec4643dd13c061eac6fc',
                                'setup_script': None,
                            },
                            {
                                'order_index': 7,
                                'question_type': 'text',
                                'difficulty': 'hard',
                                'prompt': 'Which command shows inode usage rather than disk space usage?',
                                'answer_hash': 'a6e26c579dc38f6cb533cef2f633b286f29c06ff13ac16fc539434901379d757|a6e26c579dc38f6cb533cef2f633b286f29c06ff13ac16fc539434901379d757',
                                'setup_script': None,
                            },
                        ],
                    },
                ],
            },
            {
                'order_index': 4,
                'title': 'Master',
                'description': 'Disks, systems, networking, packages, and security hardening.',
                'lessons': [
                    {
                        'order_index': 1,
                        'title': 'The Filesystem Hierarchy — /etc, /var, /home',
                        'blocks': [
                            {"type": "text", "heading": "One Tree, Deep Meaning", "body": "You already know Linux presents a single tree starting at /. What you may not know is that the top-level directories aren't arbitrary — they follow the Filesystem Hierarchy Standard (FHS), a convention every mainstream distribution obeys. Once you know the map, you can find things on any Linux machine you've never touched."},
                            {"type": "text", "heading": "The Directories That Matter", "body": "/etc holds configuration files — plain text, editable, versionable. /var holds variable data: logs (/var/log), mail spools, caches. /home holds users' personal files. /bin and /usr/bin hold user binaries; /sbin and /usr/sbin hold system binaries. /tmp is world-writable scratch space, wiped on reboot. /dev holds device files. /proc is a virtual filesystem exposing kernel and process information as readable files."},
                            {"type": "text", "heading": "Why /etc Being Text Matters", "body": "On Windows, configuration hides in binary registries and proprietary formats. On Linux, nearly everything is a text file in /etc — which means you can read it, grep it, diff it, back it up, and version it with the same tools you already know. 'Configuration as plain text' is arguably the single most important design decision in Linux system administration."},
                            {"type": "text", "heading": "The Security Lens", "body": "For a pentester, this hierarchy is a treasure map: /etc/shadow holds password hashes, /etc/passwd enumerates users, /var/log/auth.log records logins, /etc/cron* lists scheduled jobs that might be misconfigured. For a defender, it's a hardening checklist: correct permissions on /etc/shadow, sane cron entries, watched logs. Same knowledge, two sides."},
                            {"type": "practice", "command": "ls /etc | head -20", "instructions": "List the first twenty configuration files in /etc — recognize that they're all plain text."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'What is the name of the standard that defines the purpose of each top-level Linux directory? (three-letter abbreviation)',
                                'answer_hash': 'e7f291cc715ebb317b1624b027609dfbd5703df3ff57b6d748cb389f27fbebc0',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which top-level directory holds system-wide configuration files?',
                                'answer_hash': 'b7d64a9221007dfd5390f7df6cd5b8f3ea4f82faa1237141e35ebf161f5511a1|398496a8379bbcdf97125b68c283cab1a77539d7b1d6df8413195623b510af73|175ab01246347ee3cb3ad67cd8f359e5bdd765f7751c692026b7e782a3fa53ef',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': "Which top-level directory holds variable data like logs and mail spools?",
                                'answer_hash': '3b325109deb02ebf8150c4cc76e908d55f977082fe74bfd455e298770351b77d|a537daec5a632c5cd3c135caf2e220a3ae9bf53f3c5651014f1de12608a93c7e|4f6e51046147df3e0036fdf1101e2897b78604ec90303a9711242eb4c14f836c',
                                'setup_script': None,
                            },
                            {
                                'order_index': 4,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which top-level directory holds users\' personal files and settings?',
                                'answer_hash': '4ea140588150773ce3aace786aeef7f4049ce100fa649c94fbbddb960f1da942',
                                'setup_script': None,
                            },
                            {
                                'order_index': 5,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which virtual filesystem exposes kernel and process information as readable files? (starts with /)',
                                'answer_hash': '71ad1dfa1de556decbd6d7314196552e349d66067b49ab6bf8d4865faa663441|38b5e99819552be8fa8f8316d5ef09ef77277fbd7c82b6484c0dd98a4c04474d',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 2,
                        'title': 'File Editors — nano and vi',
                        'blocks': [
                            {"type": "text", "heading": "Why Editors Matter", "body": "Editing config files is half of system administration, and on a server there is no GUI — only terminal editors. You need exactly two: nano because it's forgiving, vi (or vim) because it's everywhere. nano is preinstalled or one apt install away on nearly every distribution; vi is POSIX-mandated, meaning it exists on every Unix-like system ever built, including minimal rescue environments where nothing else does."},
                            {"type": "text", "heading": "nano — The Friendly One", "body": "nano filename.txt opens the file. You type, arrows move the cursor, and the bottom two lines show the key bindings: ^O means Ctrl+O (write out — save), ^X means Ctrl+X (exit), ^K cuts a line, ^W searches. Every action is visible on screen at all times, which is why nano is the recommended first editor for beginners."},
                            {"type": "text", "heading": "vi — The Modal One", "body": "vi operates in modes, and this is the concept that confuses every newcomer: in normal mode, keys are commands, not text — x deletes a character, dd deletes a line, u undoes. Press i to enter insert mode and actually type text. Press Escape to return to normal mode. Type :w to save (write), :q to quit, :wq to do both, :q! to quit without saving."},
                            {"type": "text", "heading": "Why Bother With vi at All", "body": "Because one day you'll be in a crashed system's recovery shell or a tiny container where nano doesn't exist and vi does. Also, vi's editing language scales: once learned, commands compose (d3w deletes three words; :%s/old/new/g replaces across the whole file). Many professionals graduate to vim or Neovim and never leave."},
                            {"type": "text", "heading": "Editing Privileged Files", "body": "System files in /etc are owned by root, so you edit them with sudo: sudo nano /etc/hosts. Prefer sudoedit /etc/hosts (or sudo -e) when available — it runs your editor unprivileged on a temp copy and installs the result as root, which avoids running an entire editor with root power."},
                            {"type": "practice", "command": "nano ~/notes.txt", "instructions": "Open a file with nano, type a line, save with Ctrl+O and exit with Ctrl+X."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which beginner-friendly terminal editor shows its key bindings at the bottom of the screen? (accepts an older alias too)',
                                'answer_hash': 'f7a5936c485e5b92df267d9c20243b07a7aa2ba25ade3b0bcae88eec83168762|9ea2483b344bb5c59f34a4b43ef6bc9d5ac9bd4e0370e4b1b90a1a416b0b28cd',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'In vi, which key returns you to normal (command) mode from insert mode?',
                                'answer_hash': 'b3140286ac71ad2acf69681f4f2a907b0b83d8edfbffdd4e0a38c05a23180495|177b7cb0686749afeb39817e294fe04d1a4b59a2841ed24dc027cafecad04b48',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'In nano, which key combination saves (writes out) the current file?',
                                'answer_hash': 'ec061d7c174b1f1b5b516bb1944efc47bcb595522beb66818dcdf48b1f947e31|6d37bb0611be4f7daa7e3a337569260a24ef87b1fdc3270687650f4454c7cb6a|da9156114f140b45981cb93215a8b8ebc3ec286f724e1f83ceafed511c40bc5d',
                                'setup_script': None,
                            },
                            {
                                'order_index': 4,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'In vi normal mode, which command quits without saving changes? (include the colon)',
                                'answer_hash': '8e35c2cd3bf6641bdb0e2050b76932cbb2e6034a0ddacc1d9bea82a6ba57f7cf|d61d8fde520b10bfa36754f855a12a1797d96d7209364a471a64141e275a9ced',
                                'setup_script': None,
                            },
                            {
                                'order_index': 5,
                                'question_type': 'text',
                                'difficulty': 'hard',
                                'prompt': 'Which command safely edits a root-owned file by running your editor unprivileged on a temporary copy? (one word, or the sudo flag equivalent)',
                                'answer_hash': 'b56a93f752d254ad196f1e2c5226a8442f71f97bf23968b62ff311b01dfd6e9d|67e4810e7b96f64a33d54f112b58d5bd2199acfcfc5b4ea9ad7ec62b215aa06c',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 3,
                        'title': 'Scheduling with cron — The Backup Script',
                        'blocks': [
                            {"type": "text", "heading": "cron — The Clockwork Daemon", "body": "cron is the classic Unix scheduler: a background daemon that wakes every minute and runs whatever jobs are due. Jobs are defined in crontab files — one per user (edit yours with crontab -e), plus system-wide files in /etc/crontab and /etc/cron.d/. Each line has five time fields (minute, hour, day-of-month, month, day-of-week) followed by the command to run."},
                            {"type": "text", "heading": "Reading a cron Schedule", "body": "`0 2 * * *` means 2:00 AM every day. `*/15 * * * *` means every 15 minutes. `0 4 * * 0` means 4:00 AM on Sundays. The fields use * (any value), commas for lists (1,15), hyphens for ranges (1-5), and steps (*/10). Time fields are deceptively simple and the source of countless scheduling bugs — read them right-to-left when in doubt."},
                            {"type": "text", "heading": "The Classic Backup Script", "body": "A nightly backup is the canonical cron job: a script that runs `tar -czf /backup/home-$(date +\u2026).tar.gz /home` (date-substamped filename), or rsync to a second disk. System-wide jobs live in /etc/cron.d/ files; user jobs in crontab. Either way, check success — cron is silent when things fail."},
                            {"type": "text", "heading": "cron's Quiet Failure Mode", "body": "A cron job has no terminal. Its stdout/stderr are silently discarded — unless you redirect them. The standard pattern: append `>> /var/log/myjob.log 2>&1` to the cron command line so output and errors accumulate in a log you can actually check. An unlogged backup job is an unverified backup job."},
                            {"type": "text", "heading": "Root's crontab and Security", "body": "Jobs in root's crontab run with full root privileges — which also makes them a classic privilege-escalation target: if a root cron job executes a script that a normal user can edit, that user can add commands and become root on the next run. On a pentest, /etc/crontab and /etc/cron.* are standard enumeration targets for exactly this reason. Defensive rule: root cron scripts must be owned by root and not writable by anyone else."},
                            {"type": "practice", "command": "crontab -l", "instructions": "List your current crontab (likely empty — that's the point; check what exists before adding)."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': "Which command opens your user's crontab for editing? (full command with flag)",
                                'answer_hash': 'a9382b96f8521bff98c14c315ce899ad3b53852af837dd720915e6ff8b589836',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'In a cron schedule line, which field position (1–5) controls the day of the week? (just the number)',
                                'answer_hash': 'ef2d127de37b942baad06145e54b0c619a1f22327b2ebbcfbec78f5564afe39d',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'hard',
                                'prompt': "Which directory holds system-wide cron job files that any admin can drop a schedule into? (the base name, e.g. without trailing slash)",
                                'answer_hash': 'c374eea599bb3c50ed4432ef57aee1263cdc3c83d1c1a3c4d7e19eef1af8439b',
                                'setup_script': None,
                            },
                            {
                                'order_index': 4,
                                'question_type': 'text',
                                'difficulty': 'hard',
                                'prompt': "Why does a cron job's output usually vanish, and where should you send it? (name the standard destination pattern)",
                                'answer_hash': '2642b5d63833864f9c0c6138c0a17d8c320ddd6258dfcdaf7a05abd9fbf24a8a',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 4,
                        'title': 'Disk Management — Partitioning, Formatting, fstab',
                        'blocks': [
                            {"type": "text", "heading": "Beyond df and du", "body": "The Advanced room taught you to monitor disk space. Managing disks goes further: creating partitions (dividing a disk into sections), formatting them with a filesystem, mounting them into the tree, and making mounts persist across reboots. This is a daily task for sysadmins and a frequent exam topic for every Linux certification."},
                            {"type": "text", "heading": "Partitioning — fdisk and parted", "body": "fdisk /dev/sdb opens an interactive partition editor: n creates a new partition, p prints the table, w writes changes to disk. parted does the same job with a scriptable interface. Rule zero: triple-check the device name — partitioning the wrong disk destroys its data, and Linux will not ask twice."},
                            {"type": "text", "heading": "Formatting — mkfs", "body": "A partition is just reserved space until you build a filesystem on it: mkfs.ext4 /dev/sdb1 creates an ext4 filesystem (the Linux default). Alternatives: XFS (RHEL's default, good for large files), VFAT/FAT32 (for cross-system USB drives), swap (virtual memory)."},
                            {"type": "text", "heading": "Mounting and /etc/fstab", "body": "mount /dev/sdb1 /mnt/data attaches the formatted partition to the tree at /mnt/data; umount detaches it. To make the mount survive reboots, add a line to /etc/fstab: device (preferably by UUID — get it from blkid or lsblk -f, since device names can change between boots), mount point, filesystem type, options (defaults), then the dump and fsck pass numbers (0 0 for non-boot data disks)."},
                            {"type": "text", "heading": "The fstab Gotcha", "body": "A bad fstab line can hang the boot or drop you into an emergency shell. Use `mount -a` after editing fstab — it mounts everything fstab lists without rebooting, so you find mistakes immediately, not at the next boot. Backups of disk work: Timeshift and Clonezilla take full-system snapshots; rsync handles file-level rotation (see the ssh/rsync lesson later this room)."},
                            {"type": "practice", "command": "lsblk", "instructions": "List block devices and their mount points — identify your root disk before you ever partition anything."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which interactive command edits a disk\'s partition table? (the classic MS-DOS-style tool)',
                                'answer_hash': '0a57179c5eb4478bcd9817930ed78955908f4af413dbc327dc9272fff467b008',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which command family creates a filesystem on a partition? (four letters, with the type as a suffix like .ext4)',
                                'answer_hash': '3f5e076a40597b89ecde712c4a3c351826e0cd6055c3e7d6dc5501941e6b4633',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which command attaches a filesystem to a directory in the tree?',
                                'answer_hash': 'd4536f2555836b0b1bdc536c56e6f7245a2e89dd20ff8df68ade3cf0e7f39a65',
                                'setup_script': None,
                            },
                            {
                                'order_index': 4,
                                'question_type': 'text',
                                'difficulty': 'hard',
                                'prompt': "Which command prints the UUID of block devices — the stable identifier fstab entries should use? (accepts the lsblk variant too)",
                                'answer_hash': 'f55704d6f73c83879a92a50f496dc39635eb246c8c4781eb54eac19b12141128|9779e129f73e2318a5a40429862c1e270fb1ab4303bd3d9090729e0025f32d1d',
                                'setup_script': None,
                            },
                            {
                                'order_index': 5,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which command mounts everything listed in /etc/fstab without rebooting — the safe check after editing it?',
                                'answer_hash': 'd4536f2555836b0b1bdc536c56e6f7245a2e89dd20ff8df68ade3cf0e7f39a65',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 5,
                        'title': 'Services and systemd — start, stop, enable',
                        'blocks': [
                            {"type": "text", "heading": "What systemd Is", "body": "systemd is the first process (PID 1) on virtually every modern distribution — after the kernel boots, systemd starts everything else: services (web servers, SSH, databases), mount handling, logging (journald), and scheduling (timers). It replaced the older System V init scripts with unit files: declarative configs describing what to start and when."},
                            {"type": "text", "heading": "Unit Files", "body": "The most common unit type is the .service file. Your own units live in /etc/systemd/system/; distribution-shipped ones in /usr/lib/systemd/system/. A minimal unit defines [Unit] (Description=), [Service] (ExecStart= the command to run, Restart=on-failure), and [Install] (WantedBy=multi-user.target — what 'enable' hooks into)."},
                            {"type": "text", "heading": "The verbs you'll use daily", "body": "systemctl status nginx — is it running? systemctl start|stop nginx — right now. systemctl restart nginx — full stop and start; systemctl reload nginx — re-read config without dropping connections (where supported). systemctl enable nginx — start at boot; disable reverses it. enable does not start the service now, and start does not make it boot-persistent — most services need both."},
                            {"type": "text", "heading": "Finding and Troubleshooting Units", "body": "systemctl list-units --type=service shows loaded units and their states; systemctl list-unit-files shows every installed unit and whether it's enabled. When a service fails, journalctl -u nginx -n 50 --no-pager prints its last 50 log lines — this plus status output solves most service problems."},
                            {"type": "text", "heading": "After Editing a Unit File", "body": "systemd doesn't watch unit files. After creating or editing one, run systemctl daemon-reload so systemd re-reads its configuration — forgetting this is the classic 'I changed the file but nothing happened' mistake."},
                            {"type": "practice", "command": "systemctl list-units --type=service --no-pager | head -15", "instructions": "List loaded services on this system and note which ones are active (running)."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which systemctl verb shows whether a service is currently running?',
                                'answer_hash': '073c1634c496cdb649d1afe0a312bbb4b7e1741b271542e4a436c3b8824b1761',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which systemctl verb makes a service start automatically at boot?',
                                'answer_hash': 'e97166b54500da3a32eae48afe8df0970b19abfde3e4f3a50206cd8509feb161',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which systemctl verb starts a service right now?',
                                'answer_hash': 'cced28c6dc3f99c2396a5eaad732bf6b28142335892b1cd0e6af6cdb53f5ccfa',
                                'setup_script': None,
                            },
                            {
                                'order_index': 4,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which systemctl verb stops a running service?',
                                'answer_hash': '6c45cb72a36e63d522aa54ed8adbd7a29a989474f2f77e0458af8800564ef3cb',
                                'setup_script': None,
                            },
                            {
                                'order_index': 5,
                                'question_type': 'text',
                                'difficulty': 'hard',
                                'prompt': 'Which systemctl subcommand lists all installed unit files and whether each is enabled?',
                                'answer_hash': '8211c7038487ccea2e1372a121c68ce9e50a29574fca6e388cf1b2ed93e9cbb6',
                                'setup_script': None,
                            },
                            {
                                'order_index': 6,
                                'question_type': 'text',
                                'difficulty': 'hard',
                                'prompt': 'After editing a .service file, which systemctl command makes systemd re-read its configuration? (with the hyphen)',
                                'answer_hash': 'abb60b2783ce3ea3d11680ad761b443dc090affaa44fb1e28f8eb14f82c4a69f',
                                'setup_script': None,
                            },
                            {
                                'order_index': 7,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'In which directory do locally-created unit files belong? (starts with /)',
                                'answer_hash': '822eaa5daa513a88fa268a3a9b4cb4cd8631d9579865ab093c942e97cb81dfff|6cbfb2f9bc07cdf7cdeff217cce7ecdc609526c2d7a3d73539fea14ae24809ea|0d8a7fc1df65f3435cf6c702954994bd17a898f3f7beb66082c28a068025d547',
                                'setup_script': None,
                            },
                            {
                                'order_index': 8,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'What is the most common systemd unit type for a background daemon? (the file extension without the dot)',
                                'answer_hash': '9df6b026a8c6c26e3c3acd2370a16e93fffdc0015ff5bd879218788025db0280',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 6,
                        'title': 'Monitoring — free, uptime, lsof',
                        'blocks': [
                            {"type": "text", "heading": "Memory: free", "body": "`free -h` shows RAM and swap in human-readable units. The key column is available — memory actually free for new programs — not free, which excludes memory the kernel uses as cache (and releases on demand). A healthy Linux system normally shows small 'free' and large 'available'; panicking over low free is the classic beginner misread."},
                            {"type": "text", "heading": "Load: uptime", "body": "`uptime` prints how long the system has been running plus load averages for the last 1, 5, and 15 minutes. Load is the count of processes running or waiting to run, averaged; on N CPU cores, sustained load around N is fully busy, well above N means work is queuing."},
                            {"type": "text", "heading": "Disk: df and du — Already Your Tools", "body": "You met df and du in the Advanced room's Disk Usage lesson; here they join the monitoring toolkit: df -h for filesystem capacity, du -sh for directory sizes. A three-line monitoring script (free -h, uptime, df -h) covers the vitals of most small servers — and is a common first automation project."},
                            {"type": "text", "heading": "lsof — Everything Open", "body": "`lsof` lists every open file — and on Linux that includes sockets and device files. `lsof -i :22` shows which processes hold port 22; `lsof +D /var/log` shows who has log files open; `lsof -u dave` lists everything a user has open. When something is 'in use' and nothing obviously holds it, lsof is the answer."},
                            {"type": "text", "heading": "A Quick Health Check", "body": "Standard triage order: uptime (is load insane?), free -h (is memory exhausted?), df -h (is a disk full?), then top for the culprit. This sequence, run reflexively, resolves most 'the server is slow' reports."},
                            {"type": "practice", "command": "free -h && uptime && df -h /", "instructions": "Run the three-vital health check: memory, load, and root filesystem capacity."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which command reports memory and swap usage?',
                                'answer_hash': 'ad95d5fa651ba86d8923fe1238d24a4f1988a752acfe426ac72ac7c04471bc17',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which command shows how long the system has been up plus load averages?',
                                'answer_hash': 'dd291cd6294bafef2a7e9c378eb320e87198d6dae214272addb569775750c802',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'In free output, which column shows memory genuinely available for new programs (not the misleading one)?',
                                'answer_hash': 'ddd9818abacfde7afed60c93129175401439367a77e69ea93e0ddb3bb38e0bd9',
                                'setup_script': None,
                            },
                            {
                                'order_index': 4,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which command lists which processes have which files, directories, or sockets open?',
                                'answer_hash': 'cb298bd94fae6f2f713a1108a16e0632f3a1e21820a288d7ea86c8b00a4d4fef',
                                'setup_script': None,
                            },
                            {
                                'order_index': 5,
                                'question_type': 'terminal',
                                'difficulty': 'medium',
                                'prompt': 'Run the command that shows which processes hold port 22 open. What did you type? (accepts the ss variant too)',
                                'answer_hash': 'a31fe9656fc8d3a459e623dc8204e6d0268f8df56d734dac3ca3262edb5db883',
                                'setup_script': None,
                            },
                            {
                                'order_index': 6,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'On a 4-core machine, what sustained load average indicates the CPUs are fully busy? (just the number)',
                                'answer_hash': '4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a',
                                'setup_script': None,
                            },
                            {
                                'order_index': 7,
                                'question_type': 'text',
                                'difficulty': 'hard',
                                'prompt': "A user says the server is slow. What is the conventional first command in triage — the one that reports load?",
                                'answer_hash': 'dd291cd6294bafef2a7e9c378eb320e87198d6dae214272addb569775750c802',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 7,
                        'title': 'Users and Groups — Full Lifecycle',
                        'blocks': [
                            {"type": "text", "heading": "Recap and the Goal", "body": "The Advanced room introduced users and groups conceptually. Here's the full admin lifecycle: create accounts (useradd -m -s /bin/bash alice), set their passwords (passwd alice), add them to groups (usermod -aG developers alice), create groups (groupadd developers), and inspect the result (id alice)."},
                            {"type": "text", "heading": "Primary vs Supplementary Groups", "body": "Every user has exactly one primary group (in /etc/passwd; new files they create belong to it) plus any number of supplementary groups (in /etc/group; extra permissions). -aG appends supplementary groups; -g changes the primary. -a without -G in usermod replaces groups instead of appending — the classic accidental-removal mistake."},
                            {"type": "text", "heading": "The Files Behind It", "body": "/etc/passwd holds account records (one line per user, colon-separated: name, UID, GID, home, shell). /etc/shadow holds password hashes, readable only by root. /etc/group maps groups to members. Directly editing these files works but is error-prone; prefer the useradd/usermod/groupadd tooling."},
                            {"type": "text", "heading": "Best Practices", "body": "Give each human their own account (no shared logins — accountability dies). Prefer group-based permissions over per-file exceptions. Use sudo for privilege, never shared root passwords. Remove or lock departing users' accounts immediately (usermod -L locks the password; userdel -r removes the account and home)."},
                            {"type": "text", "heading": "Password Aging", "body": "`chage -l alice` lists a user's password aging policy; chage -M 90 alice forces a change at most every 90 days. Whether your organization rotates passwords or not, knowing where the policy lives is part of the security basics in this room's final lessons."},
                            {"type": "practice", "command": "id", "instructions": "Show your own UID, primary group, and supplementary groups."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which command creates a new user account? (accepts the Debian interactive variant too)',
                                'answer_hash': '270c557d4e3510f1330e3c69641b4842b6227407ed0642d13988fdfadf69e52c|3f43c80ed9b4bbc5106d1c0498e6fdbfc475fde4bdee86ef8f1fc4ea7c3c0f21',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which command modifies an existing user account (e.g. adding group membership)?',
                                'answer_hash': 'c765cf8f41e29c8470d5714fe762924172e7f24bc23fdfcf9512624d145760e4',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which command creates a new group?',
                                'answer_hash': '9fcab588d3c8af793c956e2a491a8f51174ecc2d0347ff018b25a3486d31ddb5',
                                'setup_script': None,
                            },
                            {
                                'order_index': 4,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which single command shows a user\'s UID, primary group, and all supplementary groups? (no arguments needed for yourself)',
                                'answer_hash': 'a56145270ce6b3bebd1dd012b73948677dd618d496488bc608a3cb43ce3547dd',
                                'setup_script': None,
                            },
                            {
                                'order_index': 5,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'New files a user creates belong to which kind of group — primary or supplementary?',
                                'answer_hash': '986a1b7135f4986150aa5fa0028feeaa66cdaf3ed6a00a355dd86e042f7fb494',
                                'setup_script': None,
                            },
                            {
                                'order_index': 6,
                                'question_type': 'text',
                                'difficulty': 'hard',
                                'prompt': 'Which command lists (or with flags, sets) a user\'s password aging policy?',
                                'answer_hash': '4abe5468f6d2cb04bb4c8a944038120037bd3e1f0ea1eea53b4b7c0f02258432',
                                'setup_script': None,
                            },
                            {
                                'order_index': 7,
                                'question_type': 'text',
                                'difficulty': 'hard',
                                'prompt': "Which usermod flag combination appends a supplementary group instead of replacing the list? (flag plus letter, e.g. -aG)",
                                'answer_hash': '0056ae649e558cefa0b81aeef123bdc5ac7613ed0e46af018c5bb63112ce9070|bc2a05403439d824923a14f8cb0b496d07a06a299eb0996efa4eb721b88dc1ce|ab81f331b638de849c6d010ab947a6c332cfb9596c0fea4d2e164c830915d6f2',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 8,
                        'title': 'Linux Networking — ip, nmcli, /etc/hosts',
                        'blocks': [
                            {"type": "text", "heading": "Configuring Addresses", "body": "You already read interfaces with ip addr show; configuring them at the desktop level is usually done through NetworkManager's command line: nmcli. `nmcli device show` lists devices and their settings; nmcli con add/con up manage saved connection profiles. Servers often skip NetworkManager entirely and use distro-specific config (Ubuntu's netplan YAML, RHEL's ifcfg files) that render into the kernel's ip layer. You may still see ifconfig in old tutorials — it's the legacy net-tools tool, superseded by ip (e.g. ifconfig's eth0 info is now ip addr show eth0)."},
                            {"type": "text", "heading": "Name Resolution — The Two Files", "body": "Two flat files matter constantly. /etc/hosts maps names to IPs locally — checked first, no DNS server involved, perfect for small labs (add `192.168.1.50 myserver` and you can ssh myserver). /etc/resolv.conf lists the DNS servers the resolver queries. nsswitch.conf decides the lookup order between them."},
                            {"type": "text", "heading": "Querying DNS Properly", "body": "You met nslookup in the Networking path; dig is the professional tool: `dig example.com` returns a structured answer with the resolved A record, the server that answered, and query timing. `dig +short example.com` gives just the address — perfect for scripts. `dig -x 8.8.8.8` does a reverse lookup (IP to name)."},
                            {"type": "text", "heading": "Why This Matters for Security", "body": "Attackers poison /etc/hosts to redirect trusted domains to malicious IPs, and defenders check it during incident response for the same reason. resolv.conf pointing at an unexpected resolver is a classic persistence/exfiltration trick. Knowing what these files should contain is knowing when something's wrong."},
                            {"type": "practice", "command": "dig +short example.com", "instructions": "Resolve a domain to its bare IP address with dig."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which NetworkManager command-line tool manages connection profiles on desktop Linux?',
                                'answer_hash': 'd97d15bc0e7aae83314b6a1b754948208fae8e750b6c24f016352036ff00e86b',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which flat file maps hostnames to IP addresses locally, before DNS is consulted? (full path)',
                                'answer_hash': '4a666ea3a3b04a24f574974df10592d51bd191614ee41b02d09f6d13c0c2f52a|9d52768bf1e23378f9d2027518552a6e0cb75b167b8e0b552835efd807be392a|3f9b62107b102ff38cd5adbb29d771a9ce5cb65b47e19b506511cac70e3b9ff2',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which file lists the DNS servers your system queries? (full path)',
                                'answer_hash': '95f03ffa45a7d998216b9e8338782aff0bc5793a5fc051549c62696540724d5e|3256d68465cbd98c21bcc28e5cbc357e8ea615e4336f211da206b11831cf4ea8|4619031467337fd042a42521a188476ea31c339587bc0219b4f2fa931dc40e89|ecd3b27977d0354e4fa2e79bc34f07067689a394711b45aa65a4dcbe9e22dc06',
                                'setup_script': None,
                            },
                            {
                                'order_index': 4,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which DNS query tool returns structured answers and supports +short for script-friendly output?',
                                'answer_hash': 'ebbde58a4bbe357e599b29131e48c6f883a9cb7003571bf54243391a4f80aacf',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 9,
                        'title': 'SSH Hardening and Secure File Transfer',
                        'blocks': [
                            {"type": "text", "heading": "The Remote Administration Protocol", "body": "SSH is how every Linux server is managed remotely — and one of the most exposed services on the Internet. Intermediate room's basics (connect, keys, scp) assumed a default configuration. Hardening it is the real skill: sshd_config is the control panel."},
                            {"type": "text", "heading": "Key-Based Authentication", "body": "You already know ssh-keygen generates a pair and ssh-copy-id installs the public key into the server's ~/.ssh/authorized_keys. Beyond convenience, disable password authentication entirely (PasswordAuthentication no) — then brute-force logins become impossible, because there is no password to brute-force."},
                            {"type": "text", "heading": "The Four Hardening Moves", "body": "In /etc/ssh/sshd_config: (1) PermitRootLogin no — attackers know root exists on every system; disable direct root login and force them to also guess a username. (2) PasswordAuthentication no — keys only. (3) AllowUsers alice dave — an explicit allowlist of who may log in at all. (4) Port 2222 — changing the port stops most Internet background noise (a real but minor win; the first three are the security). Restart sshd after any change — and keep a second session open while testing, or a mistake locks you out."},
                            {"type": "text", "heading": "scp, sftp, and rsync", "body": "scp (covered in Intermediate) moves files over SSH; sftp gives you an interactive FTP-like session over the same SSH transport — handy for browsing a remote tree. rsync is the industrial-strength sibling: rsync -avz source/ user@host:/dest/ copies efficiently over SSH (-e ssh by default), transferring only what changed (delta transfer) and mirroring deletions with --delete. The trailing-slash distinction matters: source/ copies the directory's contents; source copies the directory itself."},
                            {"type": "text", "heading": "Tunnels and Firewalls Preview", "body": "ssh -L 8080:localhost:80 user@host forwards local port 8080 through the tunnel to the server's port 80 — reaching a service that listens only on the server's loopback. Server-side, ufw allow 22/tcp opens SSH through the firewall (ufw is the Ubuntu frontend; the next-but-one lesson covers firewalls properly)."},
                            {"type": "practice", "command": "cat /etc/ssh/sshd_config | grep -v '^#' | grep -v '^$' | head -20", "instructions": "View the active (non-comment) lines of this machine's SSH server configuration."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which command generates an SSH key pair? (with hyphen, or two words)',
                                'answer_hash': 'a24f7bf3c615ad233a251863a4ed0db7f5f286205ea837daddc21bdcce35b907|b7f1c3b0229f3d915f7607166082090b3a6fc51eaf233e74f554b71bfeaf6eeb',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which file holds a user\'s authorized public keys on the server? (the filename in ~/.ssh/)',
                                'answer_hash': '2840f169a04216b746cebbd2091601b252e7fcb8126de59b6097c9c843f177d7',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which sshd_config directive, set to no, prevents direct root login?',
                                'answer_hash': 'e8da7db0895e420ed35179b666779cd0032c44c71791840f5871253f62faf58e|60ac51736a245d1be8e6f58d358ca66e62e0ebe71a2c5c0b29cff2ffb488a878',
                                'setup_script': None,
                            },
                            {
                                'order_index': 4,
                                'question_type': 'text',
                                'difficulty': 'hard',
                                'prompt': 'Which sshd_config directive restricts login to an explicit list of users?',
                                'answer_hash': '9f7b1b84f828571dc06c3cc045c9a243875c37355ce64d645707d7de10285daf',
                                'setup_script': None,
                            },
                            {
                                'order_index': 5,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which tool synchronizes directories efficiently by transferring only the changed parts of files?',
                                'answer_hash': '8ff8d40e4a4c726df40795e3134432ac66f7d055d54639c1026e341b6d2bd6e7',
                                'setup_script': None,
                            },
                            {
                                'order_index': 6,
                                'question_type': 'text',
                                'difficulty': 'hard',
                                'prompt': "What is rsync's efficiency mechanism called — transferring only differences instead of whole files? (one hyphenated or spaced term)",
                                'answer_hash': '4f4a9410ffcdf895c4adb880659e9b5c0dd1f23a30790684340b3eaacb045398|af1fbfd418119659c16c46ce72fa2cc7e179be33698719ba443b5d456b8fe38a|1658ddc8289039e08abac35db3708526c562b08dde01a07ec965f5250b0407d4|3a8bb17501315e092a4f3c78d500406936d5e031901ef8ebb9d1a32f8b2cb944',
                                'setup_script': None,
                            },
                            {
                                'order_index': 7,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which ssh flag creates a local port forward, e.g. ssh -N -L 8080:localhost:80 user@host? (just the letter flag for local)',
                                'answer_hash': '8d29a0f35918ca625667b2858e1c366e227ecbb424c5b30d008a1b2ec709e6d2',
                                'setup_script': None,
                            },
                            {
                                'order_index': 8,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which ufw verb opens a port through the firewall, e.g. ufw ___ 22/tcp? (one word)',
                                'answer_hash': '410083735735a10e658a19edd1704e606c9dd112e225825b63fafeded766c8b9',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 10,
                        'title': 'Package Management — apt, dnf, and Source',
                        'blocks': [
                            {"type": "text", "heading": "Why Package Managers Exist", "body": "Installing software on Linux isn't downloading random executables — it's resolving dependencies. Every program needs libraries, and libraries need other libraries. A package manager tracks it all: what's installed, which versions, what depends on what. The two families: Debian/Ubuntu use .deb packages with apt; Red Hat/Fedora/CentOS use .rpm with dnf (formerly yum; SUSE's zypper is the sibling)."},
                            {"type": "text", "heading": "apt — The Debian Workflow", "body": "`sudo apt update` refreshes the package index from configured repositories (metaphor: checking the store's price list — it installs nothing). `sudo apt upgrade` upgrades installed packages to newest available versions. `apt search nginx` finds packages by keyword; `apt show nginx` details one; `sudo apt install nginx` installs it plus its dependencies; `sudo apt remove nginx` uninstalls (purge also deletes config)."},
                            {"type": "text", "heading": "Repos, PPAs, and Trust", "body": "Repositories are defined in /etc/apt/sources.list and /etc/apt/sources.list.d/. Ubuntu adds PPAs — third-person archives for software Canonical doesn't ship. Every package is GPG-signed; the signature chain is what makes installing from the Internet safe. Adding a repo means trusting its maintainer with root on your machine — treat third-party repos as a security decision, not a convenience."},
                            {"type": "text", "heading": "Holding and Pinning", "body": "`sudo apt-mark hold nginx` freezes a package at its current version so upgrades skip it — useful when a new version breaks your deployment. apt-mark unhold reverses it. (dnf versions this with versionlock.)"},
                            {"type": "text", "heading": "Snap, Flatpak, and Source", "body": "Snap and Flatpak are universal package formats bundling their dependencies — sandboxed, distro-agnostic, larger. Installing from source is the last resort: download the tarball, ./configure, make, sudo make install — flexible but unmanaged (no dependency tracking, no updates; the package manager doesn't know it exists). Prefer managed packages whenever one exists."},
                            {"type": "practice", "command": "apt list --installed 2>/dev/null | head -15", "instructions": "List installed packages on this system (first fifteen) and note the name-version format."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which apt command refreshes the package index from repositories (installs nothing)?',
                                'answer_hash': '2937013f2181810606b2a799b05bda2849f3e369a20982a4138f0e0a55984ce4',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which apt command upgrades installed packages to their newest available versions?',
                                'answer_hash': '7fef9479c8bc5a3c86891cb82969cbf2ffc73c7350366c82286345d8292eebf5',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which apt subcommand finds packages by keyword?',
                                'answer_hash': '2419329067823cab5b4e5ac5dd18a6abf1f57f45e753f5fc934292f3085a3717',
                                'setup_script': None,
                            },
                            {
                                'order_index': 4,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which apt subcommand lists installed packages? (two words including the flag)',
                                'answer_hash': 'a330395cc0a53ad1207736546afff4735940937564bbf75ce1edad40780d9139',
                                'setup_script': None,
                            },
                            {
                                'order_index': 5,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': "What is the Red Hat family's modern package manager called? (three letters)",
                                'answer_hash': '40db3e70e48fe4664f019f39fc6a95a211595c7359b3a325ee62b239152b35b1',
                                'setup_script': None,
                            },
                            {
                                'order_index': 6,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which SUSE-family package manager is the sibling of apt and dnf? (six letters)',
                                'answer_hash': 'a4e7ca760018f9a5cc43601641e593b2763ab34bf85aebbea9762ca27530907e',
                                'setup_script': None,
                            },
                            {
                                'order_index': 7,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which command freezes a package at its current version so upgrades skip it? (apt-mark + one word)',
                                'answer_hash': 'e8b22d83b417e85ba4f24101a49a49cc3246a5e5e4ce6574623063e4e32801e0',
                                'setup_script': None,
                            },
                            {
                                'order_index': 8,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'In a source build, which tool actually compiles the software after ./configure?',
                                'answer_hash': 'd05aa2a15fb3c40efeeb03bec445393f00074484cf01c8fb2da90ca6695a5531',
                                'setup_script': None,
                            },
                            {
                                'order_index': 9,
                                'question_type': 'text',
                                'difficulty': 'hard',
                                'prompt': 'Which low-level Debian tool installs a single .deb file directly, without dependency resolution? (five letters)',
                                'answer_hash': '7c81d9b601bc4d2ac702a75821dae25d92432341d98f14e2a453dbc6cbeeaacb',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 11,
                        'title': 'System Security Basics',
                        'blocks': [
                            {"type": "text", "heading": "The Right Mindset", "body": "Security on Linux isn't a product you install once — it's a set of habits: least privilege, updated packages, watched logs, and a firewall that says no by default. This lesson gives you the working toolkit; each topic deserves deeper treatment elsewhere on the platform."},
                            {"type": "text", "heading": "Your Audit Trail", "body": "/var/log/auth.log records every login attempt and every sudo use. `who` shows who's logged in right now; `last` reads the login history (wtmp); `lastlog` shows each user's most recent login; `lastb` lists failed login attempts (btmp). An Internet-facing SSH server receives thousands of brute-force attempts daily — you'll see it immediately in these logs, which is exactly the point of looking."},
                            {"type": "text", "heading": "Fail2Ban — Automated Response", "body": "fail2ban watches log files and automatically bans IPs that fail repeatedly: it reads jail configs (defaults in /etc/fail2ban/jail.conf, overrides in jail.local/ and jail.d/), enables the sshd jail out of the box on Ubuntu, and turns brute-force bots into firewall-blocked addresses after a handful of tries. It pairs with the SSH hardening from the previous lesson: keys-only authentication removes the password those bots are guessing."},
                            {"type": "text", "heading": "Account Lockout and Password Policy", "body": "Beyond fail2ban, account-level controls matter: usermod -L locks a password (a ! appears in /etc/shadow's hash field), passwd -l does the same, and chage sets aging policy. If your threat model includes stolen passwords, combine password policy with the keys-only SSH posture — then there is no password left to steal."},
                            {"type": "text", "heading": "Mandatory Access Control", "body": "Traditional Unix permissions answer 'who may read this file'. SELinux (Red Hat family) and AppArmor (Ubuntu/SUSE) go further — confining what each program may touch, no matter who runs it: a compromised nginx can only access what nginx's profile allows. Ubuntu ships AppArmor enforcing profiles for key services by default (aa-status shows the picture); SELinux uses modes: Enforcing, Permissive (log only), Disabled."},
                            {"type": "text", "heading": "The Firewall — Default Deny", "body": "ufw makes firewall rules readable: `ufw default deny incoming`, `ufw allow 22/tcp`, `ufw allow 80/tcp`, `ufw enable` — done. Default-deny plus explicit allows for only what the server truly offers is the entire philosophy. iptables/nftables are the underlying machinery (firewalld is RHEL's frontend); ufw is where to start."},
                            {"type": "text", "heading": "Your Hardening Checklist", "body": "A minimal baseline for any new server: keys-only SSH with root login disabled (previous lesson), ufw default-deny with explicit allows, automatic security updates (unattended-upgrades), fail2ban on exposed services, and logs you actually read. Every item here is verifiable with commands you now know — that's the difference between reading about security and practicing it."},
                            {"type": "practice", "command": "tail -5 /var/log/auth.log 2>/dev/null || journalctl -n 5 --no-pager", "instructions": "Read the last few authentication events on this system."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which log file records login attempts and sudo usage? (full path)',
                                'answer_hash': '0d1af57f863ec17d744cbcc9efb1a12eb58daceea0bcd978c0cb0f8b01755122|710df1ff512b31b34d95a494ea025328addcca6235ff050732f1f1e687af3caf|530fce1edf3480d6f9f3a3a4fb6422c9792ed31a8e8146dd68da07bc0a1c56de',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which command shows who is logged in right now? (two letters)',
                                'answer_hash': '6ed0337140bd32b4adc5000f76333bd8ca6b2b2c9e0bc354335cf341456290e8',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which command reports the most recent login of every user, including users who have never logged in?',
                                'answer_hash': '511e7653b85653b195598a09e6515c37d1b905e1f977483f9224d543859d5801',
                                'setup_script': None,
                            },
                            {
                                'order_index': 4,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': "Which tool watches logs and automatically firewall-bans IPs that fail logins repeatedly? (one hyphenated word)",
                                'answer_hash': 'db693ea4e168c178ed7cf38224ae20ea59171238ddda09ce0187ce8dc326efa2',
                                'setup_script': None,
                            },
                            {
                                'order_index': 5,
                                'question_type': 'text',
                                'difficulty': 'hard',
                                'prompt': 'In which configuration file (or drop-in directory) do fail2ban\'s jail settings live under /etc/fail2ban/?',
                                'answer_hash': 'e8c695ad8e50c31bf0bb1432c647ed54041abfa44809d7144d4cb10b0cc9f8f8|44ee0283add0b12d540de37f2f0a514cd43483ff90d1ad373e702969ce6cbc28|03b9a879dd246a2ae2ca96b4982bd37e80fd72c9ea4a535676ea67df6444ebf6|bf42b7d94209cdd0541f5434de940b01d2362c8acde07bc584193c31b6a936b7|eb2459a097e2be11ec6a65254cc6b9a1abb972e63c0b65d9e4c86414f9a05c4f',
                                'setup_script': None,
                            },
                            {
                                'order_index': 6,
                                'question_type': 'text',
                                'difficulty': 'hard',
                                'prompt': 'Which Mandatory Access Control system does Ubuntu ship by default, confining programs with per-application profiles? (one word)',
                                'answer_hash': 'd0027c78ecb989d678c106e44210f6eac076a46d74431b4e4d4b01dee07fd235',
                                'setup_script': None,
                            },
                            {
                                'order_index': 7,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which ufw verb blocks a port, e.g. ufw ___ 23/tcp? (one word — the opposite of allow)',
                                'answer_hash': '3026a0ca485e5831657ba0120fa8dd66b3425427bfb0a2be0db743e2305cc7c5',
                                'setup_script': None,
                            },
                            {
                                'order_index': 8,
                                'question_type': 'terminal',
                                'difficulty': 'hard',
                                'prompt': 'Which command lists failed login attempts from the btmp log? (the base command name)',
                                'answer_hash': '5f74a23ea3550a0d1f8fbabe76aae57c64f7020e1317300b60f6bc716b215068|b617f42361c5a9311fa128f5dba48be3205ad81a44e87431cba572a9e588dd15|be3d2ac8b5c033e95db53843e33b64a5bbd2288cc458fa686e96e4b4b5bee9e0',
                                'setup_script': None,
                            },
                        ],
                    },
                ],
            },
        ],
    },
    {
        'slug': 'networking-fundamentals',
        'title': 'Networking Fundamentals',
        'description': 'Understand TCP/IP, subnetting, VLANs, routing, and essential protocols.',
        'icon': '/Networking.jpg',
        'order_index': 2,
        'rooms': [
            {
                'order_index': 1,
                'title': 'Network Foundations',
                'description': 'What a network is, how the Internet fits together, and how addresses work.',
                'lessons': [
                    {
                        'order_index': 1,
                        'title': 'How the Internet Works',
                        'blocks': [
                            {"type": "text", "heading": "What Is a Network?", "body": "A network is simply two or more computers connected so they can exchange data. Your home Wi-Fi is a network; the Internet is a network of networks — hundreds of thousands of smaller networks (ISPs, companies, datacenters) all agreeing to talk to each other using the same rules."},
                            {"type": "text", "heading": "The Rules: TCP/IP", "body": "For two machines to communicate, they need shared rules: how to address each other, how to split data into pieces, how to detect errors. That family of rules is the TCP/IP protocol suite. Every device on the Internet speaks it — your phone, a server in another country, a security camera."},
                            {"type": "text", "heading": "Packets", "body": "Data sent over a network is chopped into small chunks called packets. Each packet carries a piece of the payload plus a header — addressing information that lets routers forward it toward its destination. Packets from one message may take different paths and are reassembled at the far end."},
                            {"type": "text", "heading": "IP Addresses", "body": "Every device on an IP network needs an address, the same way a house needs a street address. An IPv4 address is a 32-bit number, usually written as four numbers separated by dots (e.g. 192.168.1.10). The newer IPv6 uses 128 bits because the world ran out of IPv4 addresses."},
                            {"type": "text", "heading": "Why This Matters for Security", "body": "Almost every offensive or defensive technique starts with the network: scanning for live hosts, reading packet captures, understanding which service sits behind which port. You cannot reason about attacks without a mental model of how packets move."},
                            {"type": "practice", "command": "ip addr show", "instructions": "Run ip addr show in the terminal to see your machine's network interfaces and their IP addresses."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'What is the global network of interconnected networks that all communicate using the TCP/IP protocol suite called?',
                                'answer_hash': '3b0fe0d342e9fa16a5c68dbba33f2e63c024f72a9d4c1ce1028570101d5229ff',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'How many bits long is an IPv4 address?',
                                'answer_hash': 'e29c9c180c6279b0b02abd6a1801c7c04082cf486ec027aa13515e4f3884bb6b',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 2,
                        'title': 'IP Addresses & the Loopback Interface',
                        'blocks': [
                            {"type": "text", "heading": "Anatomy of an IPv4 Address", "body": "An address like 192.168.1.10 has two parts: the network portion (which network it belongs to) and the host portion (which machine on that network). The subnet mask, e.g. 255.255.255.0, defines where the split happens. Machines on the same network can talk directly; different networks need a router between them."},
                            {"type": "text", "heading": "Interfaces", "body": "Your machine doesn't have one IP address — each network interface has one. A physical Ethernet or Wi-Fi card is an interface, but Linux also creates virtual ones. Run ip addr show and you'll see them listed: each with a name, a hardware (MAC) address, and its IP configuration."},
                            {"type": "text", "heading": "The Loopback Interface", "body": "Every Linux machine has a special virtual interface named lo — the loopback. Traffic sent to it never leaves the machine; it loops right back. The standard loopback IPv4 address is 127.0.0.1, known by the hostname localhost. It's how a program talks to another program on the same machine."},
                            {"type": "text", "heading": "The 127.0.0.0/8 Range", "body": "The entire 127.x.x.x range is reserved for loopback, but 127.0.0.1 is the conventional choice. In security work you'll constantly see services bound to 127.0.0.1 — that means they're reachable only from the machine itself, never from the network. A database listening only on loopback is invisible to attackers on the network."},
                            {"type": "text", "heading": "Private Address Ranges", "body": "Besides loopback, three ranges are reserved for private networks and are never routed on the public Internet: 10.0.0.0/8, 172.16.0.0/12, and 192.168.0.0/16. Your home router almost certainly hands out 192.168.x.x addresses. Recognizing these on sight is a basic pentest skill — they tell you what kind of network you're looking at."},
                            {"type": "practice", "command": "ping -c 3 127.0.0.1", "instructions": "Ping the loopback address. It always answers — you're testing your own machine's network stack."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'terminal',
                                'difficulty': 'easy',
                                'prompt': 'Run ip addr show in the terminal. Which IPv4 address is assigned to the loopback interface? (just the number)',
                                'answer_hash': '12ca17b49af2289436f303e0166030a21e525d266e209267433801a8fd4071a0',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'terminal',
                                'difficulty': 'easy',
                                'prompt': 'Still in ip addr show output: what is the name of the loopback interface? (the short name)',
                                'answer_hash': '9294ab38039f60d2ec53822fb46b52c663af7ea478f4d17bf43da44ede5e166c',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 3,
                        'title': 'Subnet Masks & CIDR',
                        'blocks': [
                            {"type": "text", "heading": "Where the Network Ends", "body": "A subnet mask answers one question: how many bits of an IP address identify the network, and how many identify the host? In 255.255.255.0, the first 24 ones are the network portion — so the last 8 bits name machines on that network. Two machines can talk directly only if their network portions match."},
                            {"type": "text", "heading": "CIDR Notation", "body": "Writing 255.255.255.0 as /24 (\"slash twenty-four\") is CIDR notation: the number of 1-bits in the mask. /8 is 255.0.0.0, /16 is 255.255.0.0, /32 is a single address. Every address you'll ever see in a scan report, a firewall rule, or a bug bounty scope uses this notation — reading it fluently is non-negotiable."},
                            {"type": "text", "heading": "Counting Hosts", "body": "A /24 leaves 8 host bits: 2^8 = 256 addresses. Subtract the network address (all host bits 0) and the broadcast address (all host bits 1) and you get 254 usable hosts. The same math in the other direction: a /30 has 2 host bits = 4 addresses = 2 usable — which is exactly why /30s were traditionally used for point-to-point router links."},
                            {"type": "text", "heading": "Sizing a Network", "body": "Choosing a subnet is a capacity decision: how many machines must fit? Need 50 hosts? A /26 (2 usable^6-2 = 62) fits with room to spare. Need 300? A /23 (510) or /24 is too small — /24 gives 254. This sizing logic shows up constantly in cloud networking, where VPC subnets are chosen exactly this way."},
                            {"type": "text", "heading": "Why Attackers Care", "body": "Scanning a /24 means at most 254 possible targets; a /16 means 65,534 — a very different time budget for a scan. And network boundaries are trust boundaries: a flat /16 with everything reachable is a much juicier post-exploitation target than a segmented network where each /24 is isolated behind a firewall."},
                            {"type": "practice", "command": "ip addr show | grep 'inet '", "instructions": "List your interfaces' addresses with their CIDR prefix lengths — how many host bits does each have?"}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Write the subnet mask 255.255.255.0 in CIDR notation (just the number, with the slash).',
                                'answer_hash': 'c8be8722ce1e552022c4f9e2b8a03655dacb5ec543cc8297cc8e2fb303f54aa3',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'How many bits of a /24 address identify the host?',
                                'answer_hash': '2c624232cdd221771294dfbb310aca000a0df6ac8b66b696d90ef06fdefb64a3',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'How many usable host addresses does a /30 subnet provide?',
                                'answer_hash': 'd4735e3a265e16eee03f59718b9b5d03019c07d8b6c51f90da3a666eec13ab35',
                                'setup_script': None,
                            },
                            {
                                'order_index': 4,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which of these ranges is a private (non-routable) range: 172.16.0.0/12, 172.32.0.0/12, or 169.254.0.0/16?',
                                'answer_hash': '59fb47b55edaafdb39c6a47128a8156ab33ea55dd29ebb53b4e3bd0c3900ba34|b4b5ff6c295dce73d0d12b02e74438c348689741495d0f9b7586dd6c2e7a3635',
                                'setup_script': None,
                            },
                            {
                                'order_index': 5,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'In the network 192.168.1.0/24, what is the first usable host address?',
                                'answer_hash': 'c5eb5a4cc76a5cdb16e79864b9ccd26c3553f0c396d0a21bafb7be71c1efcd8c',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 4,
                        'title': 'DHCP & NAT',
                        'blocks': [
                            {"type": "text", "heading": "Getting an Address Automatically", "body": "Every device that joins a network needs an IP address, subnet mask, default gateway, and DNS server. Typing them by hand for every laptop and phone would be impossible, so DHCP (Dynamic Host Configuration Protocol) hands them out automatically the moment a device connects."},
                            {"type": "text", "heading": "The DORA Dance", "body": "Getting a lease is four broadcast steps, remembered as DORA: the client broadcasts a DISCOVER, any DHCP server answers with an OFFER of an address, the client broadcasts a REQUEST for the offer it liked, and the server ACKs — leasing the address for a set time. Releases and renewals keep the pool from running dry."},
                            {"type": "text", "heading": "Rogue DHCP", "body": "Because DISCOVER is a broadcast with no authentication, any machine on the network can answer it. A rogue DHCP server can hand out a gateway and DNS of the attacker's choosing — silently routing every victim's traffic through a man-in-the-middle. Switches defend against this with DHCP snooping, which only lets trusted ports answer."},
                            {"type": "text", "heading": "NAT: One Address, Many Machines", "body": "Private addresses (10.x, 172.16-31.x, 192.168.x — defined in RFC 1918) can't be routed on the Internet, so your router rewrites them: outbound packets get their private source swapped for the router's public IP, with a table remembering which internal machine sent what, so replies find their way back. That translation is Network Address Translation, and it's why one public IP serves a whole household."},
                            {"type": "text", "heading": "NAT: Shield and Obstacle", "body": "NAT is accidental defense: unsolicited inbound packets match no table entry, so they're dropped — your internal machines are invisible. It's also an obstacle for attackers: a reverse shell from inside NAT reaches out and comes back through the table, which is why implants call home rather than waiting to be connected to. Port forwarding punches deliberate holes when a service must be reachable."},
                            {"type": "practice", "command": "ip route", "instructions": "Your default gateway (the 'default via' line) is almost certainly your DHCP-issued router doing NAT for you."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'On which UDP port does a DHCP server listen?',
                                'answer_hash': '49d180ecf56132819571bf39d9b7b342522a2ac6d23c1418d3338251bfe469c8|7cab7f32bd24e61b9779543c7b6436529ed6b483662c52c7deb5ea8d6a6b7be1|bc5334ccbe3820e5a19dbb5869557c9714e23e26cfb5978a0128cc7236ae2712',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'In the DHCP DORA sequence, which message does the server send right after receiving the client\'s DISCOVER?',
                                'answer_hash': '988180bf0c9328c9e8bd082755c647048ae82481fd06799bad05f2e1a4e1339c|ef0d2d43f06b676039e43f8e5dde86d9cf70b6730b4d437cb2de460762077d1d|99c62e5d516f3659771d0801868b450e3ff1d165d85a544cf664ba35fee9c0e9',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which document defined the private address ranges 10.0.0.0/8, 172.16.0.0/12, and 192.168.0.0/16? (the RFC number)',
                                'answer_hash': '329606963c38fd9e8a10b6572d6fced701be785f21a0e17c6a8d85f58493cdd1|2ab999fd9e4a9f53f480e77e332a2fc543f565775f0f91020edae34706bbf104',
                                'setup_script': None,
                            },
                            {
                                'order_index': 4,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which device performs NAT, rewriting private source addresses to its public IP on the way out?',
                                'answer_hash': '74c95604043427f0bee1d0e16bfa53afd537f736ad0073c4cc4e1ccb3a82b5dc',
                                'setup_script': None,
                            },
                            {
                                'order_index': 5,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Defenders split a network into smaller, isolated zones to contain breaches and protect critical assets. What is this practice called? (one word)',
                                'answer_hash': '47bc7ad0baa3c915759077b06ade062cd3a3dac86c92ad0dca11e31dd043e8fa|fba586be3b6f140b30389654d548a660d3a746cf8344ab6f39248caf65e2da4d',
                                'setup_script': None,
                            },
                        ],
                    },
                ],
            },
            {
                'order_index': 5,
                'title': 'Attacks by Layer',
                'description': 'The OSI model as an attack map: every layer has its own weapons.',
                'lessons': [
                    {
                        'order_index': 1,
                        'title': 'The OSI Model — An Attack Map',
                        'blocks': [
                            {"type": "text", "heading": "Why a Model", "body": "The OSI model slices networking into seven layers, from physical copper (1) to the application (7). Its real power is diagnostic: 'can you ping it?' and 'does the port answer?' are questions about different layers, and knowing which layer failed cuts troubleshooting time enormously. In security, the model becomes something sharper — an attack map."},
                            {"type": "text", "heading": "The Layers That Matter Most", "body": "Layer 2 (data link) is where switches and MAC addresses live — and where ARP spoofing and MAC flooding happen. Layer 3 (network) routes packets — IP spoofing lives here. Layer 4 (transport) handles TCP/UDP — SYN floods exhaust connection tables here. Layer 7 (application) is where actual software talks — SQL injection and XSS live here."},
                            {"type": "text", "heading": "Two Attackers, Same Stack", "body": "A SYN flood and an SQL injection both 'attack a network' — but they live four layers apart and need completely different defenses. Lower-layer attacks (2–4) target infrastructure and are usually stopped by switches, routers, and firewalls. Application attacks (7) sail straight through a perfect firewall, because they arrive as legitimate traffic. Defense in depth means different controls at each layer."},
                            {"type": "text", "heading": "The Mental Habit", "body": "When you meet any network technology, ask two questions: which layer does it live on, and who attacks that layer? Spanning tree (2) gets you rogue root bridges. DNS (7) gets you cache poisoning. The layer number is not trivia — it predicts both the attack and the control that stops it."},
                            {"type": "practice", "command": "ping -c 2 127.0.0.1", "instructions": "A successful ping proves layers 1–3 are working to that destination. When troubleshooting, always find the highest layer that works — the fault lives just above it."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'How many layers does the OSI model have? (the number)',
                                'answer_hash': '7902699be42c8a8e46fbbb4501726517e86b22c56a189f7625a6da49081b2451|3ba8d02b16fd2a01c1a8ba1a1f036d7ce386ed953696fa57331c2ac48a80b255',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'ARP spoofing operates at which OSI layer? (the number)',
                                'answer_hash': 'd4735e3a265e16eee03f59718b9b5d03019c07d8b6c51f90da3a666eec13ab35|0c6eea24ed5f3274df121af2d789e43839b3bcfb328db8deb86b46896d57be67|8a1cee436cbac1489a1883c9d886fcfc46f302c55ed4106ae31729e4f4eb9041',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'SYN floods exhaust connection tables at which OSI layer? (the number)',
                                'answer_hash': '4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a|9a3f33bc2c218fc2b637b390cf4d40a674b4700471306f655e30f2242cbbce20|9f102fe3a7d618f9960701e25169aff66169d27e1d7dcf220124a9bf2047436d',
                                'setup_script': None,
                            },
                            {
                                'order_index': 4,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'SQL injection attacks targets at which OSI layer? (the number)',
                                'answer_hash': '7902699be42c8a8e46fbbb4501726517e86b22c56a189f7625a6da49081b2451|392dfd28f10a6128a570d1e52d69b9ae836f09f2623f2ab0517cec268c8c3675|031b52ffd3cdb68797252799e42588772700c8d8ba43b644d074a2feba14fb9e',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 2,
                        'title': 'IPv6 — The Unmonitored Protocol',
                        'blocks': [
                            {"type": "text", "heading": "128 Bits, Different Rules", "body": "IPv4 addresses are 32 bits — about 4.3 billion, long exhausted. IPv6 expands the space to 128 bits: addresses like 2001:db8::8a2e:370:7334. It ships with features IPv4 bolted on later, and every modern OS runs both stacks simultaneously — dual-stack. Your machines have IPv6 addresses whether or not you planned for them."},
                            {"type": "text", "heading": "The Stealth Vector", "body": "Here's the uncomfortable pattern: most enterprise monitoring, firewalls, and IDS rules were written for IPv4. Traffic over IPv6 — especially the link-local fe80::/10 addresses that every interface auto-configures — frequently passes unlogged. Attackers know this: unmonitored protocol + auto-configured addresses = a quiet lane into networks that look hardened. Security teams that ignore IPv6 are defending half their network."},
                            {"type": "text", "heading": "Seeing Your Own IPv6", "body": "ip -6 addr show lists your IPv6 addresses. Everything starting with fe80: is link-local — valid only on the local segment, auto-generated from the MAC address, and never routed. Global addresses (starting 2xxx: or 3xxx:) are routable. The link-local address is exactly the one attackers abuse for local attacks that never touch IPv4 monitoring."},
                            {"type": "text", "heading": "The Defender Checklist", "body": "Treat IPv6 as mandatory curriculum: firewall rules for v6 (a default-deny ip6tables policy), monitoring for Neighbor Discovery (IPv6's ARP equivalent), and RA guard against rogue router advertisements. If your nmap sweep only covered IPv4, you mapped half the target."},
                            {"type": "practice", "command": "ip -6 addr show", "instructions": "List your IPv6 addresses. Identify which one is link-local (starts with fe80) and which, if any, is global."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'How many bits long is an IPv6 address? (the number)',
                                'answer_hash': '2747b7c718564ba5f066f0523b03e17f6a496b06851333d2d59ab6d863225848',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Every IPv6 interface auto-configures an address starting with fe80. What kind of address is this called? (hyphenated)',
                                'answer_hash': '6064640044b6aa881fb94ec61b949b948b58b8089a71d488ce1d766ea42b58a0|708d9df31fe892b44a128161e19919b28f396634ecda9fdcfab2862de44c45b8',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Why do attackers like IPv6 in enterprise networks? In one phrase: because it is often what?',
                                'answer_hash': 'b3f459ab0f5e850b5b422df499a4de8b87a221240c6cef58c97c30ab15ae2a84|d1d422cef6848ea02852c7733acc01d9f809f5f8bd3d7c08a4560914baca9644|92581da3a3b1d27d28f2dccc30a85929d6615949c81fd3b9eb84e79839543ef5',
                                'setup_script': None,
                            },
                            {
                                'order_index': 4,
                                'question_type': 'terminal',
                                'difficulty': 'medium',
                                'prompt': 'Show your IPv6 addresses with the ip command (the -6 flag does it). What did you type?',
                                'answer_hash': 'ef0c6a93b51501280edb5aa78f9b5dc025fc3ba6ee90401a0a995f7f02a17a99|e1789c3b727f87ff5a204febdaf4345a3a846593a4d1d22adcc2318bd80423f1|60089d0466368c95412dab09579a7d7331fe43764181f85298d2c3e6b6b84538|0b531d1687f186f674f6e5233a78e5ebbe2f2c18dcff750f519029fed0e41dbf',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 3,
                        'title': 'Attacking DNS',
                        'blocks': [
                            {"type": "text", "heading": "The Favorite Target", "body": "DNS was designed for a trusting Internet, and it shows. Every attack in this lesson exploits one design assumption: that DNS answers can be believed. For a pentester, DNS is also the cheapest recon source there is — most organizations publish an enormous amount about themselves in their own records."},
                            {"type": "text", "heading": "Zone Transfers (AXFR)", "body": "A zone transfer is a full copy of a domain's DNS database, meant for backup nameservers only. Ask politely: dig AXFR example.com @ns1.example.com. If the server answers — and misconfigured ones still do — you receive every subdomain, every address: the target's internal naming scheme handed over in seconds. It should always be restricted; testing it is a standard first check."},
                            {"type": "text", "heading": "Cache Poisoning", "body": "A resolver caches answers. Cache poisoning injects a forged answer into that cache — banking.com now resolves to the attacker's server, for every user of that resolver, until the cache expires. Modern resolvers randomize ports and transaction IDs to make forging hard, but the attack remains the reason DNSSEC exists."},
                            {"type": "text", "heading": "Subdomain Takeover", "body": "Companies create subdomains pointing at cloud services (app.example.com → a hosting account), then decommission the service — forgetting the DNS record. The dangling record can often be claimed by anyone who registers the now-free service account: their content is served from your domain. Trusted name, attacker's page — excellent for phishing."},
                            {"type": "text", "heading": "DNS Tunneling", "body": "Because DNS is allowed through every firewall, data can escape inside it: the attacker controls an authoritative nameserver, malware encodes stolen data into subdomain lookups (a1b2c3.exfil.example.com), the resolver forwards the queries, and the answers carry commands back. Slow, but it crosses networks with no direct Internet access. Detect it by watching for high-volume, high-entropy subdomain lookups."},
                            {"type": "practice", "command": "nslookup -type=MX example.com", "instructions": "Ask for a domain's mail records — a different record type than the A record nslookup returns by default. Record-type fluency is the basis of all DNS recon."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which DNS request type asks a nameserver for a full copy of the zone? (the four-letter code)',
                                'answer_hash': '75107a81f50bd7ec8c20472b8786a7280f9d55e60017bd6f1049fc9b7e150e5d',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'A forged answer injected into a resolver\'s cache redirects a domain to an attacker\'s server. What is this attack called? (one word)',
                                'answer_hash': 'bd624895401c0adca7b738fa02304d22a67f502bf25383ae67a82d460153f0ee|f608fcfd3673a92347f54d1ee7d4658694e2e28918c04753517d3082e2e52a35',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'hard',
                                'prompt': 'A dangling DNS record points at a decommissioned cloud service that anyone can re-register. What is this attack called? (two words)',
                                'answer_hash': '5932b2bbe74c4afaae18b853d8c4702808c9bbf42eecd3fa7a24fd9a67f8c97f',
                                'setup_script': None,
                            },
                            {
                                'order_index': 4,
                                'question_type': 'text',
                                'difficulty': 'hard',
                                'prompt': 'Exfiltrating data encoded inside DNS lookups, because DNS is allowed through every firewall, is called DNS what?',
                                'answer_hash': '8e1b0bc84f08959b7abd4c78d426fd958f2e11e3be78fdbb9bf84628edd5c3bc|4d8f931e8d604c0d1d88e5c484861597aee72bf924b6bf0304bade33997175d9',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 4,
                        'title': 'Attacking DHCP',
                        'blocks': [
                            {"type": "text", "heading": "Recall: The DORA Handshake", "body": "From Room 1: a client Discover-broadcasts, a server Offers an address, the client Requests it, the server Acknowledges. Every message in that handshake is unauthenticated — a client trusts whichever server answers, and the network accepts whatever configuration arrives. That single sentence is the entire attack surface."},
                            {"type": "text", "heading": "Rogue DHCP Server", "body": "Connect a laptop running a DHCP server to the network, answer faster than the real one, and clients take your configuration: your default gateway and DNS server. Position yourself as the gateway and every packet the victim sends transits your machine — a man-in-the-middle issued automatically, no ARP spoofing needed. Detect it: legitimate servers are known; any other DORA offer is an incident."},
                            {"type": "text", "heading": "DHCP Starvation", "body": "A different weapon: spoof thousands of MAC addresses (the chaddr field), each requesting a lease, until the real server's address pool is empty. New legitimate clients get no address at all — a denial of service. Tools automate this in minutes. Where rogue DHCP redirects, starvation simply starves."},
                            {"type": "text", "heading": "The Defenses", "body": "DHCP snooping on a switch marks trusted ports (where real servers sit) and drops OFFER/ACK arriving from untrusted ports — killing rogue servers outright. The same feature feeds Dynamic ARP Inspection, which you'll meet in Room 6. For a defender, the lesson is: the handshake's trust is a switch configuration problem, not a client one."},
                            {"type": "practice", "command": "grep -sE 'domain-name-servers|routers' /var/lib/dhcp/dhclient*.leases 2>/dev/null || echo 'no dhclient leases on this machine'", "instructions": "Look at where your own DHCP config came from. On a real network, you'd compare it against the servers that are supposed to exist."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'What does a rogue DHCP server typically hand clients to position itself for a man-in-the-middle? (the two-word config item that decides where traffic goes)',
                                'answer_hash': '876536a49fb6ef3ed9a1d0cee2fa111af3155f118d06756958e9646103aa4f30|4ea5ee68fea05586106890ded5733820bb77d919cda27bc4b8139b7cd33b8889',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'hard',
                                'prompt': 'Exhausting a DHCP server\'s address pool with spoofed MAC addresses is called DHCP what?',
                                'answer_hash': 'bdcd69991500ee75d72a981ac4c80f0c99ac493d7fe67549930534f8023c8bd5|00ed1e3432ba2e94c7260fa969ebc83c3c8d16196b76bebe4f4e668443affad8',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which switch feature blocks DHCP offers arriving from untrusted ports, defeating rogue servers?',
                                'answer_hash': '20eb878e7ffcde75616b3f75ea23dcbd880feb78a09a69f1cc63eed5b4dc2f7c|01e51dcdd9fc564577b0a1727b6c7d9aab0ad64ab88c8e20702741e04b352754',
                                'setup_script': None,
                            },
                        ],
                    },
                ],
            },
            {
                'order_index': 2,
                'title': 'Protocols & Ports',
                'description': 'DNS, TCP vs UDP, and the well-known port numbers every practitioner memorizes.',
                'lessons': [
                    {
                        'order_index': 1,
                        'title': "DNS — The Internet's Phone Book",
                        'blocks': [
                            {"type": "text", "heading": "The Problem DNS Solves", "body": "Humans remember names; computers route by numbers. You remember example.com, but your machine needs the IP address 93.184.216.34 to connect. The Domain Name System is the distributed directory that translates one into the other — and it's one of the most-queried, most-attacked protocols on the Internet."},
                            {"type": "text", "heading": "How a Lookup Works", "body": "When you type a hostname, your machine asks a resolver (usually your ISP's or a public one like 1.1.1.1). If the resolver doesn't have the answer cached, it walks the hierarchy: root servers point to the .com servers, which point to the domain's own nameservers, which finally return the record."},
                            {"type": "text", "heading": "Records", "body": "DNS stores more than name-to-address mappings. The common record types: A maps a name to an IPv4 address, AAAA to IPv6, MX names the mail servers for a domain, CNAME is an alias, and TXT holds arbitrary text — often used for proving domain ownership or anti-spam policies."},
                            {"type": "text", "heading": "DNS as an Attack Surface", "body": "Because DNS is usually allowed through every firewall, it's a favorite tunnel for attackers hiding data exfiltration inside lookups. On the recon side, enumerating a target's DNS records (subdomains, mail servers, name servers) is one of the first passive information-gathering steps in a penetration test."},
                            {"type": "practice", "command": "nslookup example.com", "instructions": "Resolve a real domain and watch which address comes back."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which protocol translates human-readable domain names into IP addresses?',
                                'answer_hash': 'dd75a9d6fb309c4399fe425cd5f90ff95eba135d6924fb91766ee5d3726b168a',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'On which well-known port does DNS typically listen?',
                                'answer_hash': '2858dcd1057d3eae7f7d5f782167e24b61153c01551450a628cee722509f6529',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 2,
                        'title': 'TCP vs UDP',
                        'blocks': [
                            {"type": "text", "heading": "Two Ways to Ship Data", "body": "The transport layer offers two main protocols, and choosing between them is a genuine engineering trade-off. TCP (Transmission Control Protocol) builds a connection first and guarantees delivery. UDP (User Datagram Protocol) just fires packets and hopes — no connection, no guarantees, far less overhead."},
                            {"type": "text", "heading": "TCP: Reliable and Ordered", "body": "TCP establishes a connection with a three-way handshake (SYN, SYN-ACK, ACK), numbers every byte it sends, retransmits anything lost, and delivers data in order. Web traffic, email, and file transfers use it because a missing or scrambled byte would corrupt the result."},
                            {"type": "text", "heading": "UDP: Fast and Cheap", "body": "UDP skips the handshake and the bookkeeping. If a video frame or a voice packet arrives late, retransmitting it is pointless — it would already be outdated. So live streaming, gaming, and VoIP prefer UDP: occasional loss is invisible, but latency is everything."},
                            {"type": "text", "heading": "The Handshake as Recon Signal", "body": "That SYN/SYN-ACK/ACK handshake is exactly what port scanners probe. A scanner sends a SYN and listens: SYN-ACK back means the port is open, RST means closed, silence usually means a firewall dropped it. Understanding the handshake is understanding how nmap decides a port's state."},
                            {"type": "practice", "command": "ss -tun", "instructions": "List active connections: -t shows TCP, -u shows UDP, -n shows numeric ports."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which transport protocol guarantees ordered, reliable delivery through a connection handshake?',
                                'answer_hash': '00645195b93272275b50a6c935a23fb62e3e793e8476e83414fed0fcdfee8b41',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Video streaming services typically build on which transport protocol, accepting occasional loss for lower latency?',
                                'answer_hash': '571e437548ffbac2cccfa26d7026aa7bd84186d79ca5ab7a5924d9026359b9e0',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 3,
                        'title': 'Well-Known Ports',
                        'blocks': [
                            {"type": "text", "heading": "Ports: Doors on a Machine", "body": "An IP address gets your packet to the right machine, but which program should receive it? Ports answer that — a 16-bit number (0–65535) attached to every packet. A web server listens on one port, a mail server on another; each conversation is tagged with a port so the operating system hands data to the right process."},
                            {"type": "text", "heading": "The Well-Known Range", "body": "Ports 0–1023 are the well-known ports, reserved by convention for standard services: 22 SSH, 25 SMTP (mail sending), 53 DNS, 80 HTTP, 443 HTTPS, 3389 RDP. Ports 1024–49151 are registered for common applications; the rest are ephemeral — used by clients for the duration of one conversation."},
                            {"type": "text", "heading": "Why Ports Matter for Offense", "body": "A port scan is a census of a machine's open doors. Each open port is a service, each service is software, and software has vulnerabilities. nmap's service version detection exists because knowing 'port 443 open' is less useful than knowing 'nginx 1.18 is answering on 443'."},
                            {"type": "text", "heading": "Ports in Defense", "body": "Defenders think in ports too: a server should expose only the handful of ports its job requires, and everything else should be closed or filtered. Spotting an unexpected open port — a database on 3306 facing the Internet — is one of the highest-value findings a quick assessment can produce."},
                            {"type": "practice", "command": "ss -tln", "instructions": "List listening TCP sockets on this machine (-l means listening) and note which ports are taken."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which port number does HTTPS use by convention?',
                                'answer_hash': '6d05621ab7cb7b4fb796ca2ffbe1a141e0d4319d3deb6a05322b9de85d69b923',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'terminal',
                                'difficulty': 'medium',
                                'prompt': 'Run nslookup example.com (or dig example.com) in the terminal. Which command did you use? (just the command name)',
                                'answer_hash': '120313e8b11d8c6c1c2608c92d35c85226728b202779f48ae543f83a14b29bdd|ebbde58a4bbe357e599b29131e48c6f883a9cb7003571bf54243391a4f80aacf',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Write the tcpdump command that shows only ICMP traffic on any interface (just the command).',
                                'answer_hash': '8a08a0928dda8095cc1088457f70e5f10d1745daa5afc5317ab0a81cebbc75dd|29618de5386ee3c08a6b8c36b6665afeda955095bd2b63b07d166dc5fa996890',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 4,
                        'title': 'ICMP — Ping and Its Cousins',
                        'blocks': [
                            {"type": "text", "heading": "The Network's Error Channel", "body": "Beneath TCP and UDP sits a third protocol with no data payload of its own: ICMP, the Internet Control Message Protocol. It carries diagnostics and error reports — 'host unreachable', 'time exceeded', 'redirect to a better route' — the network's way of telling you why something didn't work."},
                            {"type": "text", "heading": "Ping: Echo and Reply", "body": "The most famous ICMP pair is echo request (type 8) and echo reply (type 0). ping sends a request and waits for the reply, measuring the round-trip time. It's the first tool anyone reaches for when 'the network is down' — and the first data point it gives you is binary: alive or not."},
                            {"type": "text", "heading": "Reading Ping Output", "body": "Every reply line carries a time (round-trip latency) and a ttl (the reply's Time To Live, which reveals how many routers it crossed: 64 minus TTL on Linux systems). A ping to your own loopback never leaves the machine, so it shows ttl=64 with essentially zero latency."},
                            {"type": "text", "heading": "Ping in Offense and Defense", "body": "Attackers ping-sweep subnets to map live hosts before any port scan, because a reply narrows 254 candidates down to a handful. Defenders respond by rate-limiting or dropping echo requests at the perimeter — and by knowing that a silent host isn't necessarily absent: many firewalls drop ICMP while leaving TCP ports very much open."},
                            {"type": "practice", "command": "ping -c 3 127.0.0.1", "instructions": "Ping the loopback and read the ttl= value — then explain to yourself why it's 64 and not less."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which protocol carries ping\'s echo request and echo reply messages? (the acronym)',
                                'answer_hash': 'c3eac7105ca647900c32b5eced7a6ccb56cded0790ef0bc08614a5ad31e54025',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'What is the ICMP type number of an echo request?',
                                'answer_hash': '47edbc85b3b030461e2bc5b4b48e54cd4926cda85a060cd104f9c57ed43b1480|2c624232cdd221771294dfbb310aca000a0df6ac8b66b696d90ef06fdefb64a3|23cef7bf61bb5f1a483cd7dba65b616e59fe6addc840fab9770550aa9e08b2f3',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'terminal',
                                'difficulty': 'easy',
                                'prompt': 'Ping the loopback address three times. What ttl= value do the replies show?',
                                'answer_hash': 'a68b412c4282555f15546cf6e1fc42893b7e07f271557ceb021821098dd66c1b',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 5,
                        'title': 'HTTP & HTTPS — The Web\'s Protocol',
                        'blocks': [
                            {"type": "text", "heading": "Requests and Responses", "body": "HTTP is a simple, text-friendly protocol: a client sends a request — a method, a path, headers — and the server answers with a status code, headers, and usually a body. Everything the web does, from loading a page to submitting a login form, is built on this request/response cycle."},
                            {"type": "text", "heading": "Methods", "body": "The method declares intent: GET retrieves without side effects, POST submits data, PUT replaces a resource, DELETE removes one. GET parameters ride in the URL — which is why GET never should carry passwords; URLs end up in browser history, server logs, and Referer headers."},
                            {"type": "text", "heading": "Status Codes", "body": "The status code is the server's verdict: 200 OK, 301/302 redirects, 403 Forbidden (authenticated but not allowed), 404 Not Found, 500 Internal Server Error. Reading status codes instantly tells a pentester what a server is willing to discuss — a 403 on an admin path confirms it exists but is protected, while a 404 may not mean the path is absent."},
                            {"type": "text", "heading": "HTTPS = HTTP + TLS", "body": "Plain HTTP is a postcard: anyone on the path can read it. HTTPS wraps HTTP inside TLS, which encrypts the channel and authenticates the server via certificates signed by certificate authorities. HTTPS runs on port 443 by convention, HTTP on 80. Encryption protects the contents — but not the destination: the hostname still leaks to DNS and to anyone watching connections."},
                            {"type": "text", "heading": "Why Web Security Is Its Own Field", "body": "Because HTTP is everywhere and its inputs are text, it carries the web's entire attack surface: SQL injection rides in GET/POST parameters, XSS rides in response bodies, broken authentication rides in cookies and session handling. The Web App Pentesting path builds directly on this lesson."},
                            {"type": "practice", "command": "curl -sI http://example.com", "instructions": "Fetch response headers from a real site and find the status code and any interesting header fields."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which HTTP method retrieves a resource without side effects and sends its parameters in the URL?',
                                'answer_hash': '2998b3232d29e8dc5a78d97a32ce83f556f3ed31b057077503df05641dd79158',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which status code means the requested resource was not found?',
                                'answer_hash': '6b3c238ebcf1f3c07cf0e556faa82c6b8fe96840ff4b6b7e9962a2d855843a0b',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'On which port does HTTPS listen by convention?',
                                'answer_hash': '6d05621ab7cb7b4fb796ca2ffbe1a141e0d4319d3deb6a05322b9de85d69b923|f2c3253ba1bcfe3830c9e9fbe8d32f5e0ad9e602b0b921538ccc596d862f98dd|995c7361d82dffdba9e3bc27448d147b313f70a54c35cc0c7efa57aaf2fe8ccc',
                                'setup_script': None,
                            },
                            {
                                'order_index': 4,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'What does HTTPS add on top of HTTP to encrypt and authenticate the channel? (the protocol name, an acronym)',
                                'answer_hash': 'b7e651cbb43ba0ca3498759c8c3596c3a11a199004cd9e5a198d50d4585ec8c5|dc5a2e46e9ef93ecfa28d22ce4a3bca1765a20af1e7336b70bd5cab4e5590d87',
                                'setup_script': None,
                            },
                        ],
                    },
                ],
            },
            {
                'order_index': 6,
                'title': 'Appliances & the Data Link',
                'description': 'Routers, switches, firewalls, and the Layer 2/3 attacks that target them.',
                'lessons': [
                    {
                        'order_index': 1,
                        'title': 'Network Appliances — Attack Surface Mapping',
                        'blocks': [
                            {"type": "text", "heading": "The Devices Themselves Are Targets", "body": "Every appliance on a network — router, switch, firewall, load balancer, access point — runs an operating system with a web interface, SSH, and years of unpatched CVEs. Attackers don't just travel through these devices; they log into them. A compromised router sees and reroutes everything. The first question about any appliance is therefore: how do you manage it, and who else can?"},
                            {"type": "text", "heading": "The Management Plane", "body": "Appliances are managed in-band (over the same network they serve) or out-of-band (a separate management network). In-band management over Telnet sends credentials in cleartext — anyone sniffing the segment owns the device. SNMPv1/v2c authenticates with community strings, and far too many devices still answer to the defaults: public for reads, private for writes. SSH and SNMPv3 exist precisely to fix this."},
                            {"type": "text", "heading": "Defaults Kill", "body": "Internet-wide scans consistently find routers and firewalls answering on their admin interfaces with vendor default passwords — admin/admin, admin/password, or nothing at all. Shodan indexes them by the thousand. Before a single exploit is written, an attacker tries default credentials on everything: it is the cheapest win in the inventory."},
                            {"type": "text", "heading": "Mapping Your Own", "body": "The defender's exercise is uncomfortable and valuable: walk your own network and list every appliance, its management interface, its port, and how it authenticates. nmap the management VLAN from inside. The forgotten switch web UI on the default VLAN is the classic finding. Function versus attack surface, in two columns, for every device."},
                            {"type": "practice", "command": "ss -tln", "instructions": "Management interfaces are just listening ports. What is this machine exposing that it shouldn't?"}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which protocol, common on appliances, authenticates with community strings whose defaults are public and private?',
                                'answer_hash': '9e7f55c19ed75b9bb3bfcc7c65182fdeac0236803c4bf26ed437824b7338956a',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which cleartext remote protocol should never be used to manage an appliance because it sends credentials in plaintext?',
                                'answer_hash': '5a4f77d09a9b2832e2e548152026ceb71b9bcea7d2cadf4b44cc8d23c428001d',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'An attacker floods a switch\'s MAC address table with thousands of fake source addresses until the switch starts forwarding all frames everywhere. What is this attack called? (two words)',
                                'answer_hash': '36fe61e3337c305f34f131effd01974df084f8ff7f00eed1ec9e332d24c1c9da|39c44bcb804801ff17edffca381a1cd2405af1b27b1a15dc88abf22c9db433fc',
                                'setup_script': None,
                            },
                            {
                                'order_index': 4,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'The cheapest credential attack against a newly reachable appliance is trying the vendor\'s what? (two words)',
                                'answer_hash': 'fbf4363491863757ab28b80058fff24d28e3752b23b7448b2c34fd5988f3bff0|7e032a866d3ff88ab5fac35a3b19a273fca2c930083d5b3b46e7e1ac837692d8|0ba3a8508b42866780c1539e887c8daf88aa91e18581ea66e9eaaf5cf7e5b513',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 2,
                        'title': 'Load Balancers, Firewalls & Airwaves',
                        'blocks': [
                            {"type": "text", "heading": "Load Balancers: Trusting Headers", "body": "Load balancers sit in front of web farms and often rewrite what the backend sees of the client. The X-Forwarded-For header is supposed to carry the real client IP — but the client sends it too. A backend that trusts it for logging or access control can be fooled into seeing any source address the attacker types. Trusting client-controlled headers is the lesson: know which hop added the header."},
                            {"type": "text", "heading": "Origin Discovery", "body": "If only the load balancer is exposed, attackers hunt the origin: the real backend IP behind it. Leaks come from old DNS records, certificate transparency logs, misconfigured services answering directly, or the origin accepting traffic from any source rather than only the balancer. Origin lockdown (firewall to balancer-only traffic) closes most of this."},
                            {"type": "text", "heading": "Firewalls and Permitted Services", "body": "A firewall rulebase is an attack surface too. Bypass-by-design usually means riding a service that must stay open: anything tunneled over 443 crosses a rule that allows HTTPS. An overly permissive allow-any rule, or one left over from a decommissioned project, defeats the whole device. Rule review is security work, not paperwork."},
                            {"type": "text", "heading": "Wireless Attacks", "body": "An evil twin is a rogue access point impersonating a legitimate one — same SSID, stronger signal — so clients associate with the attacker instead. The deauthentication attack sends forged management frames that force clients off a network; disconnected clients often reconnect to the strongest SSID, which the attacker arranged to be. Modern WPA3 and 802.11w (protected management frames) blunt both."},
                            {"type": "practice", "command": "curl -s -H 'X-Forwarded-For: 1.2.3.4' http://example.com -o /dev/null -w '%{http_code}\\n'", "instructions": "Send an arbitrary X-Forwarded-For header to any web service — notice nothing stops you. Backends that trust it blindly are trusting the attacker."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which HTTP header, often trusted by backends to reveal the client IP, can be set to anything by the client itself? (the exact header name)',
                                'answer_hash': 'e148359b268370d4d120d732c0af32478ca550cff9fae45146cc08c867b12cd9',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'A rogue access point impersonating a legitimate network to capture client traffic is called an evil what?',
                                'answer_hash': '72b33a1cb0bfc9cdd3db0102962414c7a0d85aad94eba64cd8c33265242f7f9f|35a53abb01f049ed49f551625c5c1fc45f2381c7804aa0e13c239b1b60ceceb0',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which wireless attack sends forged management frames to force clients off a network so they reconnect to a stronger rogue SSID?',
                                'answer_hash': 'e957b0ee2f6a4d0da431714571736e26a9e3bf1caa2fc01b5d682ef3f26bc294|da26748823899561eb2a55fd5a9d867d39a9d00a942e15828438fcf9e8de3804',
                                'setup_script': None,
                            },
                            {
                                'order_index': 4,
                                'question_type': 'text',
                                'difficulty': 'hard',
                                'prompt': 'The real backend IP hidden behind a load balancer or CDN is called the what? (one word)',
                                'answer_hash': '181fdd46fc4a7246b9f4f1eba3129ba5d724011af5f10223b3589955d1df108a',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 3,
                        'title': 'VLANs and VLAN Hopping',
                        'blocks': [
                            {"type": "text", "heading": "VLANs: Networks on a Wire", "body": "A VLAN partitions one physical switch into many logical networks: finance, guests, servers — isolated at Layer 2 as if they were separate switches. Traffic between VLANs must pass through a router, where access control lives. Segmentation is the single most valuable architectural defense: a breach in the guest VLAN should not see the database VLAN at all."},
                            {"type": "text", "heading": "Trunk Links and Tagging", "body": "Switch-to-switch links (trunks) carry multiple VLANs, tagging each frame with an 802.1Q tag. The native VLAN is the one exception — its frames go untagged. That exception is where hopping attacks aim."},
                            {"type": "text", "heading": "Attack 1: DTP Exploitation", "body": "The Dynamic Trunking Protocol lets Cisco switches negotiate trunk links automatically. An attacker's machine speaking DTP to a switch port can convince the switch to form a trunk — and a trunk sees all VLANs. The fix is unglamorous and absolute: disable DTP on every port (switchport nonegotiate), and shut down every port not in use."},
                            {"type": "text", "heading": "Attack 2: Double-Tagging", "body": "Double-tagging exploits the native VLAN: an attacker crafts a frame with two 802.1Q tags. The switch strips the first (matching its native VLAN config) and forwards the second tag's VLAN unexamined — delivering the frame into a VLAN the attacker never had access to. Defenses: never use VLAN 1, set a dead VLAN as native, and don't rely on VLANs as your only isolation — L3 firewalls between segments are what actually stop crossing."},
                            {"type": "practice", "command": "ip -d link show", "instructions": "Look at link details on this machine — VLAN subinterfaces (if present) appear as NAME@PARENT, showing tagging from the host's view."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'What technology partitions a single physical switch into multiple isolated logical networks? (the acronym)',
                                'answer_hash': 'c3b258168c41c0bce97616716bef315eeed33eb1142904bfe7f32eb392c7cf80|f54fe889ea03ebf346f2ea06e6c54f865fc7aa2da928781d8df6eaee4f0b574c',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'hard',
                                'prompt': 'Which Cisco negotiation protocol can an attacker abuse to convince a switch port to become a trunk? (the acronym)',
                                'answer_hash': 'd017f5c6aad2574063e03a591e6b6266fb0e262e883a9b3e4b5302e1faf7d641',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'hard',
                                'prompt': 'Double-tagging attacks exploit frames sent untagged on which special VLAN? (two words)',
                                'answer_hash': 'e76c5e4a1839fe292bd9a7ff200f1e8bcacd590e8da75b64a6e21b25c288125b|19da09de1bafe82691d3ab6041324d8ab84375c29d75b8bc219bac4fe703adab|bef32d2c315a289576f2a6828d27edb16bb316a4d85c271f2d794045f3ea668d',
                                'setup_script': None,
                            },
                            {
                                'order_index': 4,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'What should every unused switch port be? One word: on or off?',
                                'answer_hash': 'b4dc66dde806261bdda8607d8707aa727d308cd80272381a5583f63899918467|17eb3c0168d0d7b21ede5481150f17233427d89833ec121b4dbc4fb96cfab71e|08434ba9cdf55a02284e2913400586cd289878e0f055f7bb0b07ce392caeb989',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 4,
                        'title': 'STP and Routing Protocol Attacks',
                        'blocks': [
                            {"type": "text", "heading": "STP: Order Through Elections", "body": "The Spanning Tree Protocol prevents Layer 2 loops by electing a root bridge and blocking redundant paths. The election is just whoever advertises the lowest bridge ID — there is no authentication in classic STP."},
                            {"type": "text", "heading": "The Rogue Root Bridge", "body": "Announce a bridge ID of zero and you win the election: traffic re-converges through your machine, and you now sit on paths you didn't have before — a silent, elegant wiretap. BPDU Guard on access ports is the defense: any port that sees a BPDU (which no legitimate endpoint should ever send) shuts down immediately."},
                            {"type": "text", "heading": "Routing Protocols: Trusting Announcements", "body": "Dynamic routing protocols learn the network by trusting neighbors' announcements. RIP accepts routes with (historically) no authentication at all — a rogue RIP announcement redirects traffic wholesale. OSPF neighbors authenticate (or should — misconfigured networks skip it), and BGP on the Internet fundamentally runs on trust: the 2018 interception of cryptocurrency traffic via a hijacked BGP route showed a country-level actor redirecting global address space with a fraudulent announcement."},
                            {"type": "text", "heading": "Route Injection", "body": "Injecting a rogue route — a more specific or allegedly shorter path — is the generic form of the attack: traffic follows the best announcement, and the best announcement is whatever the attacker sent. Defenses: authenticate routing protocols (OSPF MD5/SHA, RSTP BPDU protection, RPKI for BGP), filter what you accept, and monitor for routes that appear and vanish."},
                            {"type": "practice", "command": "ip route", "instructions": "Read your routing table as an attacker would: every line is an instruction the kernel trusts. Ask where each one was learned from."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which protocol\'s root-bridge election can be hijacked by announcing a bridge ID of zero? (the acronym)',
                                'answer_hash': '5a5dd437caabea5a2af2f5469aae38b3d13075b43b34267c3528c4ac63c7cd51',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'In an STP attack, the attacker takes over the election by winning the root what? (two words)',
                                'answer_hash': '655be8cc33f313fb21d80ad5fe2b6baf78ce08edaa0c2f0e5ed1c36029076ff8',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Announcing a false best path into a routing protocol so traffic follows you is called route what?',
                                'answer_hash': '545a70019936cf88744185133577a965a1b49a40a9d1be1a3b3c773a31eac2a9|cc81558648b43060f0993242b522d64a71d7793522d5393de25c59e45d963536',
                                'setup_script': None,
                            },
                            {
                                'order_index': 4,
                                'question_type': 'text',
                                'difficulty': 'hard',
                                'prompt': 'Which Internet routing protocol runs fundamentally on trust, making country-scale traffic hijacks possible? (the acronym)',
                                'answer_hash': '37ca8609324a68bb5ba8b3a26995155c7cb4cf660818b7bceeb205ef3aaa97cc|5ed8c466a446c1f9802271d7393e807a8470b936cff34f05bc617cf4d5a7dd72',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 5,
                        'title': 'ARP Poisoning and Its Defenses',
                        'blocks': [
                            {"type": "text", "heading": "Recall the Hole", "body": "Room 3 covered arp and neighbor tables; Room 1 mentioned man-in-the-middle. Now the full mechanics: ARP has no authentication. A host accepts any ARP reply it hears and overwrites its table — even replies nobody asked for (gratuitous ARP). That is not a bug to patch; it is the protocol as designed."},
                            {"type": "text", "heading": "The Poisoning Attack", "body": "The attacker broadcasts crafted ARP replies to two victims: to the gateway claiming to be the client, to the client claiming to be the gateway. Both victims update their tables and now route their traffic through the attacker — bidirectional man-in-the-middle. Tools like Bettercap automate the whole dance with one command. The victim notices nothing: everything still works, just observed."},
                            {"type": "text", "heading": "What It Enables", "body": "Positioned in the middle, an attacker can sniff credentials in cleartext protocols, strip TLS downgrade opportunities, hijack sessions, or selectively modify traffic. It only works on the local segment — which is exactly why VLAN segmentation and switch-level defenses matter so much: they fence the segment where this attack can live."},
                            {"type": "text", "heading": "The Switch Fights Back", "body": "DHCP snooping (Room 5) learns which ports legitimately hold which IPs; Dynamic ARP Inspection (DAI) uses that binding table to drop any ARP reply whose claimed IP-to-MAC pair doesn't match what DHCP actually assigned. Poisoning frames die at the port. Static-IP corners of the network need static bindings — a small operational cost for closing the classic local attack."},
                            {"type": "practice", "command": "ip neigh", "instructions": "Read your neighbor table and note the reachability states. On a real network, an entry that flips from REACHABLE to STALE to a different MAC is the fingerprint of poisoning."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which switch feature drops ARP replies whose IP-to-MAC binding contradicts what DHCP assigned? (the acronym)',
                                'answer_hash': '4de6bb4e4a6c2058981c96726e7142bc487588eadf7f315b1d7dc56e30cc51aa|605fd99b6aa7f8a61582b8b480f916e5b6f55ed5e6f3296b1c24fdd3292c9c04',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Hosts accept ARP replies and update their tables under what condition? (complete the phrase: they accept them…)',
                                'answer_hash': '783d2e6574c4abc16916162114c193d0bd25741a26cb7a61137fb8dbf994f00f|97b7e2db799e2b79e65f418b42a7d3054c95b2d3ab1dba243039597e44a38084|ef0d75f0ebdcb2b8faa2440d0ea475418d64f17191c54321000af4c4848f3862',
                                'setup_script': None,
                            },
                        ],
                    },
                ],
            },
            {
                'order_index': 3,
                'title': 'Inspecting Networks on Linux',
                'description': 'Hands-on with the tools: arp, tcpdump, ip route, and ss.',
                'lessons': [
                    {
                        'order_index': 1,
                        'title': 'The Local Segment — arp',
                        'blocks': [
                            {"type": "text", "heading": "The Missing Link: MAC Addresses", "body": "IP addresses get packets across the Internet, but on the final local network hop, delivery uses hardware addresses: MAC addresses. A MAC address is a 48-bit identifier burned into a network card, written as six hex pairs like aa:bb:cc:dd:ee:ff. The first three pairs identify the manufacturer."},
                            {"type": "text", "heading": "ARP: Address Resolution", "body": "When your machine needs to send a packet to a neighbor on the same network, it broadcasts one question: 'who has 192.168.1.1?' The machine holding that IP answers with its MAC address. The questioner caches the pairing in its ARP table so it doesn't have to ask again for every packet."},
                            {"type": "text", "heading": "Reading the ARP Table", "body": "Run ip neigh (or the older arp -n) and you'll see the neighbors your machine has actually talked to, each as an IP-to-MAC pairing with a state like REACHABLE or STALE. On a strange network, the ARP table is a quick census of who else is out there."},
                            {"type": "text", "heading": "ARP Spoofing", "body": "ARP has no authentication — any machine can answer any ARP question. An attacker who repeatedly answers 'I have the gateway's IP' with their own MAC position themselves between the victim and the rest of the network: a man-in-the-middle. Knowing this attack exists is why you should never trust ARP tables on untrusted networks."},
                            {"type": "practice", "command": "ip neigh", "instructions": "Show your machine's neighbor (ARP) table."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'How many hexadecimal digit pairs make up a MAC address?',
                                'answer_hash': 'e7f6c011776e8db7cd330b54174fd76f7d0216b612387a5ffcfb81e6f0919683',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which attack works by answering ARP requests with the attacker\'s MAC address to intercept traffic between two machines? (three words, hyphenated)',
                                'answer_hash': '739d02fa6e447dd70c27887993f4fa6054147cb8a8a438a7c158d7b092331903',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'terminal',
                                'difficulty': 'medium',
                                'prompt': 'Run the command that displays your machine\'s neighbor (ARP) table, then submit the command you used.',
                                'answer_hash': '6e4840564c20bbbbaa405be5d9c8530e812e45ffff34bc0b206a340e72001c56|ee35f0b62759f935a478333339effd44fe0d1ab043a4db37b288bcd5bcaf62fb',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 2,
                        'title': 'Capturing Traffic — tcpdump',
                        'blocks': [
                            {"type": "text", "heading": "Watching the Wire", "body": "tcpdump prints a live description of every packet crossing an interface — who talked to whom, which ports, which flags. It's the standard command-line packet sniffer, present on virtually every Unix-like system, and the fastest way to answer 'is this traffic actually flowing?'"},
                            {"type": "text", "heading": "Choosing an Interface", "body": "By default tcpdump picks the first non-loopback interface, but -i chooses explicitly: tcpdump -i eth0 watches eth0, and tcpdump -i lo watches loopback traffic — ideal for watching services talk to each other on the same machine."},
                            {"type": "text", "heading": "Filters", "body": "tcpdump's power is its filter language: tcpdump port 443 shows only HTTPS traffic, tcpdump host 10.0.0.5 only conversations with that host, and filters combine with and/or/not. A well-chosen filter turns a firehose into a needle-finder."},
                            {"type": "text", "heading": "Useful Flags", "body": "-c N stops the capture after N packets — perfect for scripted checks. -n disables name resolution (faster, and no DNS noise). -a prints payloads as ASCII, which makes plaintext protocols like HTTP readable right in the capture. On a switchless or wireless network where you can see others' traffic, tcpdump is also how credentials leak detection happens."},
                            {"type": "practice", "command": "ping -c 1 127.0.0.1 & sleep 1; tcpdump -i lo -c 4", "instructions": "Capture four loopback packets — ICMP pings will show up if you background a ping first."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which tcpdump flag stops the capture automatically after a set number of packets?',
                                'answer_hash': '0c3603e13e24a40b4bf215e3795a9a40d60a8456fb7b63c2d11e81701a231e85',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which tcpdump flag renders packet payloads as ASCII so plaintext protocols are readable?',
                                'answer_hash': 'c274891790345c56cef3b53c026bdc48150948fa60c56306073d6fea7766ad6a',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which graphical tool is the standard GUI alternative to tcpdump for deep packet analysis?',
                                'answer_hash': '28662759fcf7454b4388d4ff2798bf5c3c7dbe92090612b4214a411ea5d17cc8',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 3,
                        'title': 'Routes & Listening Sockets',
                        'blocks': [
                            {"type": "text", "heading": "The Routing Table", "body": "Your machine makes a forwarding decision for every outgoing packet: which interface, via which next hop? The kernel keeps that policy in its routing table. Run ip route and read it — one line per known destination, most specific match wins."},
                            {"type": "text", "heading": "The Default Route", "body": "The line reading default via 172.17.0.1 dev eth0 means: anything not matching a more specific line goes to 172.17.0.1 through eth0. That gateway is usually your router or container host. 'Which interface is my default route on?' is often the first question when figuring out where a machine's traffic exits."},
                            {"type": "text", "heading": "Listening Sockets", "body": "A server 'opens a port' by asking the kernel to listen on it. The ss command lists every socket: ss -tln shows TCP sockets in LISTEN state with numeric ports — in other words, the doors this machine currently holds open. Compare it against what should be running to spot surprises."},
                            {"type": "text", "heading": "Why a Pentest Starts Here", "body": "Local enumeration always includes listening sockets: services bound to 0.0.0.0 are reachable from the network, ones bound to 127.0.0.1 are local-only. That single distinction often decides whether a vulnerable service is an actual finding or a dead end."},
                            {"type": "practice", "command": "ip route && ss -tln", "instructions": "Print the routing table, then list every TCP port this machine is listening on."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'terminal',
                                'difficulty': 'medium',
                                'prompt': 'Run the ip subcommand that prints the kernel routing table. What did you type? (e.g. "ip X")',
                                'answer_hash': 'af3ce2f82176f6ff262c67dd815d4ce6e74396c33c1887d6cffc59bfb78ef80b',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'terminal',
                                'difficulty': 'medium',
                                'prompt': 'Look at the default line in ip route output: which device name does your traffic exit through?',
                                'answer_hash': '9c32a8c7e59e7935b1e5d3eea04ed8e08c41c1d3da88b98a8ad15d38cfc55b00',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'terminal',
                                'difficulty': 'medium',
                                'prompt': 'Which single command lists all listening TCP sockets with numeric port numbers? (just the command name)',
                                'answer_hash': 'a31fe9656fc8d3a459e623dc8204e6d0268f8df56d734dac3ca3262edb5db883',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 4,
                        'title': 'Ping Sweeps — Mapping Live Hosts',
                        'blocks': [
                            {"type": "text", "heading": "From One Host to a Network", "body": "pinging one address tells you one machine's state. A ping sweep pings a whole range — every address in a subnet — and collects the replies. The result is a list of live hosts: the first map an attacker draws and the first thing a defender should know about their own network."},
                            {"type": "text", "heading": "Nmap Host Discovery", "body": "nmap -sn 192.168.1.0/24 is the canonical sweep: -sn says 'do host discovery, skip port scanning'. For each address that responds, nmap prints 'Host is up'. It's fast, quiet relative to a full scan, and works on any range from /32 to /8 — change the CIDR, change the size of the hunt."},
                            {"type": "text", "heading": "Going Quiet", "body": "By default nmap may try reverse-DNS on hosts it touches; -n disables all DNS lookups, making the sweep faster and quieter — no DNS server logs your queries. Sweep output pairs naturally with grep: pipe it through grep -i up to strip away everything but the live entries."},
                            {"type": "text", "heading": "Why Defenders Run Sweeps Too", "body": "An inventory you didn't verify is a guess. Defenders run the same sweeps against their own subnets to find rogue devices, forgotten printers with default passwords, and the VM someone spun up and never patched. If a sweep finds a host you can't identify, that's an incident question, not a trivia question."},
                            {"type": "practice", "command": "nmap -sn 127.0.0.1", "instructions": "Sweep a single address to see nmap's host-discovery output format — then imagine it across a /24."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which tool is the standard choice for sweeping a subnet and listing live hosts?',
                                'answer_hash': '5286b91aa11e48184da2c742f7f08492b8be0e02c01188b55b47d4be0e23fb18',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which nmap flag performs host discovery but skips port scanning?',
                                'answer_hash': 'a3ba30081655ce871a84c9f5cba682e750f404a41b4e91008030dd5e5378105f|be0f306ab9299802efccbaaa7333dcf6ece4fd81c51cc081c952f202c3048a1b',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which nmap flag disables DNS resolution for faster, quieter sweeps?',
                                'answer_hash': '5249f4fcc629efa0e6d6b2bf746b6c5de61611ce719ad61ac820fbe5c8cece66',
                                'setup_script': None,
                            },
                        ],
                    },
                ],
            },
            {
                'order_index': 4,
                'title': 'The Journey of a Packet',
                'description': 'TTL, traceroute, and what happens between two machines.',
                'lessons': [
                    {
                        'order_index': 1,
                        'title': 'TTL — The Packet Lifespan',
                        'blocks': [
                            {"type": "text", "heading": "The Looping Problem", "body": "Routing mistakes happen: a router configured wrong can send a packet in a circle. Without a safeguard, a lost packet would circulate forever, piling up traffic. IP solves this with a simple counter in every packet header: Time To Live, or TTL."},
                            {"type": "text", "heading": "How TTL Works", "body": "The sender initializes TTL to a conventional value — Linux uses 64. Every router along the path decrements it by one. When a router receives a packet with TTL 1, it may not forward it: it drops the packet and sends back an ICMP 'Time Exceeded' message to the original sender."},
                            {"type": "text", "heading": "TTL as a Fingerprint", "body": "Because each OS picks a different starting TTL (Linux 64, Windows 128, some network gear 255), the TTL of an arriving packet is a soft fingerprint of the sender's operating system: a packet arriving with TTL 62 likely started at 64 and crossed two routers. It's cheap, noisy, but surprisingly useful in triage."},
                            {"type": "text", "heading": "The Bug That Became a Tool", "body": "That 'Time Exceeded' reply is exactly what traceroute abuses. Send a packet with TTL 1 — the first router replies. TTL 2 — the second router replies. Each increasing value maps one more hop along the path. A mistake-detection mechanism became the standard network mapping tool."},
                            {"type": "practice", "command": "ping -c 2 1.1.1.1", "instructions": "Ping a public server and read the ttl= value in the reply — estimate how many routers the reply crossed if it started at 64."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which IPv4 header field, decremented at every router hop, prevents packets from circulating forever?',
                                'answer_hash': 'd557c112e0f271127883f18b8f6be62db59d5fbdcbe7f546a1256e5bcdd6aafb',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'What starting TTL value does Linux typically set on outgoing packets?',
                                'answer_hash': 'a68b412c4282555f15546cf6e1fc42893b7e07f271557ceb021821098dd66c1b',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Windows machines typically start outgoing packets with which TTL value?',
                                'answer_hash': '2747b7c718564ba5f066f0523b03e17f6a496b06851333d2d59ab6d863225848',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 2,
                        'title': 'Traceroute — Following the Path',
                        'blocks': [
                            {"type": "text", "heading": "Turning Errors into a Map", "body": "traceroute weaponizes the TTL mechanism you just learned. It sends its first packet with TTL 1: the first router drops it and returns an ICMP Time Exceeded message — revealing router one. TTL 2 kills the packet at router two, revealing router two. Increasing TTL hop by hop, traceroute collects the entire path to a destination."},
                            {"type": "text", "heading": "Reading the Output", "body": "Each output line is one hop: a sequence number, the router's hostname and IP if resolvable, and three round-trip times (traceroute sends three probes per TTL). Lines showing only asterisks mean the hop didn't answer — routers may rate-limit or drop ICMP, so silence mid-path is normal; what matters is whether the final destination eventually responds."},
                            {"type": "text", "heading": "tracepath and Variants", "body": "tracepath does the same job without root privileges and records the path MTU along the way. traceroute -I uses ICMP echo requests instead of UDP probes — sometimes sneaking past filters that drop UDP. Different probe types reach different places; a pentester maps the same target several ways and compares."},
                            {"type": "text", "heading": "What the Map Is Worth", "body": "To an attacker, a traceroute sketches the target's edge: how many firewall hops stand in the way, which ISP carries the traffic, where load balancers appear. To a defender, traceroute from outside shows exactly what your infrastructure reveals — and often exposes out-of-band paths that shouldn't exist."},
                            {"type": "practice", "command": "traceroute 1.1.1.1 2>/dev/null || tracepath 1.1.1.1", "instructions": "Trace the path to a public resolver and count the hops before the destination answers."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which command traces the network path to a destination by exploiting TTL expiry? (just the command name)',
                                'answer_hash': '261063ce089e84d540c499ef21de9486c2be4ee6c79142a2dca537262239e6a5|70c115a748981fa96fc21d23b3de8f2b0eb2adad0c1ac3bc26ec809620169c64',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Each router along the path decreases a packet\'s TTL by what amount?',
                                'answer_hash': '6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which ICMP message does a router send back when it drops a packet whose TTL reached zero? (two words)',
                                'answer_hash': '292fb0c821308ba900e9492da52a05c9e5108be719488f13b62fc6a4a0a66cdb|fcd4b49f2886ba89c36cb398849537d6d852c4ad9fd266a8086390812f3470c2|2d229eb96474017f72b82e4a51657c34f7363fe8114c91c6a3211845cee1c277',
                                'setup_script': None,
                            },
                            {
                                'order_index': 4,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which trace tool, unlike traceroute, needs no root privileges and also reports the path MTU?',
                                'answer_hash': '70c115a748981fa96fc21d23b3de8f2b0eb2adad0c1ac3bc26ec809620169c64',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 3,
                        'title': 'The Full Journey — One Packet, End to End',
                        'blocks': [
                            {"type": "text", "heading": "Putting It All Together", "body": "You type ping 127.0.0.1, then ping a lab server, then open a web page. Every one of those is the same machinery: DNS resolves the name, ARP maps the next hop to a MAC, TCP opens a connection, IP routes the packets, TTL keeps them from circling forever, and the reply retraces everything in reverse. This lesson walks one packet the whole way — the capstone of this path."},
                            {"type": "text", "heading": "The Sending Side", "body": "The application hands over data. TCP (or UDP) wraps it in a segment with source and destination ports. IP adds source and destination addresses, a TTL, and a protocol number. The routing table picks the outgoing interface and next hop. Then ARP resolves the next hop's IP to a MAC address — unless it's already cached — and the frame hits the wire."},
                            {"type": "text", "heading": "Along the Way", "body": "Each router strips the frame, reads the destination IP, decrements the TTL, looks up its own routing table, and re-encapsulates toward the next hop. If a hop is too slow or unreachable, ICMP error messages fly back to the sender. NAT boxes rewrite addresses at the edge; firewalls drop what matches no rule."},
                            {"type": "text", "heading": "The Far End", "body": "The destination NIC receives the frame, the kernel matches the destination port to a listening socket, and the data climbs the stack: IP verifies, TCP reassembles and acknowledges, the application finally reads its bytes. A handshake began the conversation, ACKs carried it, and FIN or RST ends it. Symmetry all the way back."},
                            {"type": "text", "heading": "Why This Matters Most", "body": "Every tool in this path — ping, tcpdump, ss, traceroute, nmap — is just a different vantage point on the journey you can now trace in your head. When something breaks, you'll know which stage failed. When something attacks, you'll know which stage it abuses. That mental model is the real deliverable of this course."},
                            {"type": "practice", "command": "ping -c 2 127.0.0.1; ss -tln | head -5", "instructions": "Run both: a full round trip to your own stack, and the list of doors your machine holds open."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'What step immediately precedes a frame leaving your machine toward the next hop? (the resolution of an IP to a hardware address — two words)',
                                'answer_hash': 'cf835fc094349f22c2214fc8256cb895fcbcc01c77083c0f94114703d9e79a29|c235d32cdd061bdfe8439e9e1523a2cfac23bc76e9bf7ac634b491158c2801f1|fae1c31fabd0e93e01bb39cfcb26f82d6de7113b2d4542f712220941decd4e1d|85aadb0b53b5f0968ebc271a56dd6ce086eccae800fdf3512f7bf62005bf47b6',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'A packet goes out, a reply comes back — the path there and back is collectively called a what? (two words)',
                                'answer_hash': 'dcdd22226bc947f5071f8796d4769af5c2302717c477f1c2baed1a1f06db0675',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which TCP segment acknowledges received data and keeps the connection alive? (the acronym)',
                                'answer_hash': '64a37929fb113e18daa6263a1fb1f90c51d262552efa5a50596f5f653ba955f8',
                                'setup_script': None,
                            },
                            {
                                'order_index': 4,
                                'question_type': 'terminal',
                                'difficulty': 'easy',
                                'prompt': 'A full round trip without leaving the machine: ping which address? (just the number)',
                                'answer_hash': '12ca17b49af2289436f303e0166030a21e525d266e209267433801a8fd4071a0',
                                'setup_script': None,
                            },
                        ],
                    },
                ],
            },
            {
                'order_index': 7,
                'title': 'Enumeration, Tunnels & Filtering',
                'description': 'How practitioners scan services, tunnel through networks, and build — and bypass — firewalls.',
                'lessons': [
                    {
                        'order_index': 1,
                        'title': 'Service Enumeration — Thinking in Ports',
                        'blocks': [
                            {"type": "text", "heading": "From Port Numbers to Attack Plans", "body": "Room 2 taught what ports are; this lesson teaches what they're worth. Each well-known service carries a known attack surface: 21 FTP welcomes anonymous logins and ships credentials in cleartext; 23 Telnet is pure cleartext and should simply not exist; 161 SNMP leaks full device configs to anyone holding the community string; 445 SMB gave the world EternalBlue and usernames via null sessions; 3389 RDP is a permanent brute-force magnet."},
                            {"type": "text", "heading": "The Scanner's Toolkit", "body": "A real sweep is layered: -sn discovers live hosts, then -sS (SYN scan — never completes the handshake, so many old logs miss it) or -sT (full connect, needs no privileges) maps open ports. Add -sV to fingerprint software versions and -O for OS detection. The distinction matters to defenders too: a SYN scan and a connect scan leave completely different packet trails, and knowing what each looks like in a pcap is blue-team literacy."},
                            {"type": "text", "heading": "UDP: The Ignored Half", "body": "TCP scanning is cheap; UDP scanning is slow — no handshake means closed ports often just say nothing, so scanners wait for timeouts. Yet half the juicy services are UDP: 53 DNS, 67/68 DHCP, 161 SNMP, 5060 SIP (VoIP — recon and toll fraud). A pentest that skipped UDP would miss SNMP leaking a router config in cleartext."},
                            {"type": "text", "heading": "Banners and Fingerprinting", "body": "Many services announce their version the moment you connect — that's banner grabbing, doable by hand with nc host port. Version data turns 'port open' into 'this host runs vsftpd 2.3.4', which turns into a known-CVE lookup. Service and OS fingerprinting is the bridge between a scan and an exploit; patch levels and exposure are the defender's mirror of the same information."},
                            {"type": "practice", "command": "ss -uln", "instructions": "List listening UDP sockets on this machine — the half of the port map that TCP scans never show."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which nmap flag asks it to fingerprint the software version behind each open port?',
                                'answer_hash': '1af832b1983fe2d07b0e452da1233b5ef3396582abe43116e3ac3085360fec01',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which nmap scan type completes the full TCP handshake for every port? (flag or name)',
                                'answer_hash': 'ce09708900240337a50228379dc548866c0e5cfcf9c91c54fa7eae26cebe96f9|ec16c4b3fc6fb923e1856eea6ca045f32eda23f45f10e79fb656199c67ccfbec',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which nmap flag performs the stealthy half-open SYN scan?',
                                'answer_hash': '9e0a827a2f2719143b9fc04ef08f461cdda31914fe4fb97c8577a1edded8787d|a9206742a87cbaed4fdbeceb135ddf8702cfc79ccc55c581b5d1c12f23dd98e9',
                                'setup_script': None,
                            },
                            {
                                'order_index': 4,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'On which TCP port does SMB speak — the service behind EternalBlue and null-session enumeration? (the number)',
                                'answer_hash': '0e12831a7047f759733b21f028525039607350b1b1b4fe904595427e72ea0d9b',
                                'setup_script': None,
                            },
                            {
                                'order_index': 5,
                                'question_type': 'terminal',
                                'difficulty': 'medium',
                                'prompt': 'List all listening UDP sockets with numeric ports using ss. What did you type?',
                                'answer_hash': 'bdd792feab5f0f9e2e192dbff5f3fc888c55cd762bb37bb881bb833c24557f6e|f7ac6c5b51d8a1f5225859c9afe176f55b2761aa454e816c1408abe27d63adc2',
                                'setup_script': None,
                            },
                            {
                                'order_index': 6,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Connecting to a service by hand and reading the version string it volunteers is called banner what?',
                                'answer_hash': '48609a741803785d8f3ec0255312e9d73cbfdc086b8a2019b2fe5de37c7c942e|d1f656d859ee51e6d96bccbd2ae4c084c4c39a90d1ce53cac268de87573f87ed',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 2,
                        'title': 'VPNs and Tunneling',
                        'blocks': [
                            {"type": "text", "heading": "Why Tunnels", "body": "A VPN builds an encrypted tunnel across an untrusted network, making remote access and site-to-site linking safe over the open Internet. Two architectures matter: site-to-site (network-to-network, routers do the work invisibly) and remote-access (one user's machine joins the network from anywhere)."},
                            {"type": "text", "heading": "The Protocol Families", "body": "IPsec is the classic: IKE negotiates keys, ESP encrypts, and it runs in tunnel mode (whole IP packet encrypted — used site-to-site) or transport mode (payload only). OpenVPN wraps traffic in TLS — flexible, certificate-driven, easy to deploy, mildly slower. WireGuard is the modern entrant: a fraction of the code, kernel-fast, key-based, trivially auditable. All three do the same job with different trust mechanics."},
                            {"type": "text", "heading": "The Offensive Perspective", "body": "Post-exploitation, attackers build their own tunnels: SSH -D makes a SOCKS proxy of any compromised host, tools like Chisel wrap arbitrary traffic in HTTP, and proxychains forces any tool through the resulting chain. Each pivots you deeper — from one foothold to the next network segment. The technique is identical to the defender's VPN; only intent differs."},
                            {"type": "text", "heading": "VPN Gateways Are Targets", "body": "The appliance that terminates your VPN sits at the network edge and is exposed to the entire Internet by definition — which is why Fortinet, Pulse, and Ivanti gateway CVEs dominate breach headlines. A pre-auth RCE in the VPN is a front-door key. Defenses: patch gateways obsessively, require MFA, watch the VPN logs — and remember split tunneling means remote machines browse the web outside your protection while holding your keys."},
                            {"type": "practice", "command": "ssh -V", "instructions": "The same tool that gives you a shell also builds SOCKS proxies (-D) and port forwards (-L/-R). The most reliable pivot in the world is probably already installed on the target."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Which modern VPN protocol is famous for a tiny, auditable codebase and kernel-speed performance?',
                                'answer_hash': '28387a164997aec602d65711a6a74d4ee162d8fb5987702e7962031a61262887|999a0481871f07504a64424606b3bd0c4c26e68b5379ac3f866710549d0ff31a',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'In IPsec, which mode encrypts the entire original IP packet, header and all? (two words)',
                                'answer_hash': '94a35fdc30df7d129a447217f9ffade7e4917bdcc90460d7db2f0460c08c0e06|ceffa9e1164c96df778d3f69639e83958be009d80dd99aa92c2d522ac676d148',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Post-exploitation pivoting typically uses SSH SOCKS proxies and port what? (the -L/-R feature, two words)',
                                'answer_hash': '8e1b0bc84f08959b7abd4c78d426fd958f2e11e3be78fdbb9bf84628edd5c3bc|31da0a0e66eb655170b615730d292b34fd9dc0859fe38f80b1d4c76ec0886c14|bce5745cedeb0722ebfda1d9c043021cf65f87d158397d8656848494434032a8|94a35fdc30df7d129a447217f9ffade7e4917bdcc90460d7db2f0460c08c0e06',
                                'setup_script': None,
                            },
                            {
                                'order_index': 4,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Why are VPN gateways such high-value targets? Complete the phrase: they sit at the network what?',
                                'answer_hash': 'cb48dc2470a69641ae193cb70f642d7b794c9b3b76392576d51bac086e41e604|a1cb100f57e971cacf269e7c26e4630a25a8e9d4bdd35e32df1a80b66b896254|1b9bce4ed71bf3fa2c3ffa08efb8f9238a6a46d5e5daba847a1d46e52119b7a1',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 3,
                        'title': 'Firewalls, NAT and Egress',
                        'blocks': [
                            {"type": "text", "heading": "Rules Are Read in Order", "body": "A stateful firewall tracks every connection in a state table and evaluates each new packet against its rulebase top-down, first match wins. That makes rule order a security property: an accidental allow-any above your careful deny rules silently nullifies them. Auditing a ruleset means reading it in order, questioning every rule above the default."},
                            {"type": "text", "heading": "NAT: SNAT, DNAT and What It Hides", "body": "SNAT rewrites the source address of outgoing traffic (a whole office behind one public IP); DNAT rewrites the destination of incoming traffic — port forwarding. NAT was never a security control, but it hides internal structure: attackers see the gateway, not the topology. It also breaks logging — logs record the NAT device's IP, not the true source, unless you correlate."},
                            {"type": "text", "heading": "Egress: The Forgotten Direction", "body": "Ingress filtering gets all the attention, but attacks exit too: reverse shells call out, data exfiltrates, C2 beacons pulse. Networks that filter inbound but allow any outbound connection hand attackers a guaranteed path — an implant on a workstation can call home on any port it likes. Egress filtering (allow only what's needed out: DNS, updates, specific APIs) is what makes exfiltration hard."},
                            {"type": "text", "heading": "Bypass by Design", "body": "Anything allowed is a tunnel candidate: HTTPS (443) carries what it's told to carry, DNS carries queries — and both cross every firewall by necessity. DNS tunneling exports data one lookup at a time; a reverse shell on 443 rides the web rule. WAFs add content-level filtering for web traffic, but they miss non-HTTP tunnels entirely. Detection lives in the logs: unusual query volume, odd SNI values, beacons at machine-regular intervals."},
                            {"type": "practice", "command": "cat /proc/net/nf_conntrack 2>/dev/null | head -5 || echo 'conntrack not readable here'", "instructions": "A stateful firewall's state table looks like this. Every tracked connection is a decision the firewall already made."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'In a firewall rulebase, what property determines which rule wins when two rules match the same packet? (one word)',
                                'answer_hash': '3eeb7e96e59ce40f9cb1a089daba079fd699f6867a30f6634af8570967b2375a',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which NAT flavor rewrites the destination address of incoming traffic — the mechanism behind port forwarding? (the acronym)',
                                'answer_hash': '4aac9266bd39cf579d0613448f3d3ef8104fd4e9aa37ec956c9ef6acd601fe9e',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Outbound traffic filtering — the kind that stops reverse shells and exfiltration — is called what filtering? (one word)',
                                'answer_hash': 'a3083687ee111912f7daf2d0bfb3647c7a4ec90a05984cbdebac4203036a9735',
                                'setup_script': None,
                            },
                            {
                                'order_index': 4,
                                'question_type': 'text',
                                'difficulty': 'hard',
                                'prompt': 'Exfiltrating data one lookup at a time through a protocol every firewall allows is called DNS what?',
                                'answer_hash': '8e1b0bc84f08959b7abd4c78d426fd958f2e11e3be78fdbb9bf84628edd5c3bc|4d8f931e8d604c0d1d88e5c484861597aee72bf924b6bf0304bade33997175d9',
                                'setup_script': None,
                            },
                            {
                                'order_index': 5,
                                'question_type': 'text',
                                'difficulty': 'hard',
                                'prompt': 'A stateful firewall remembers every connection in its what? (two words)',
                                'answer_hash': '7ee3f6ba6dee3e68646f1b6c8b792c4fcddb179a03c0a12a311c3c2237b04a70|66af4c9861c6231104ef92a1403fde548e7be856fcebd42cca52b0f051bd76ea',
                                'setup_script': None,
                            },
                        ],
                    },
                    {
                        'order_index': 4,
                        'title': 'Traffic Types and Their Abuse',
                        'blocks': [
                            {"type": "text", "heading": "One-to-One: Unicast", "body": "Unicast is normal delivery — one sender, one recipient, the pattern of almost all traffic. Targeted attacks are unicast too: a scanner talks to each host individually, and a C2 channel is a private conversation. Detection baseline: unicast flows between known endpoints at known times."},
                            {"type": "text", "heading": "One-to-All: Broadcast", "body": "Broadcast reaches every host on the segment — the mechanism ARP requests and DHCP Discovery depend on. Abuse has a long pedigree: the Smurf attack of the 1990s sent a broadcast ping with a spoofed source, and thousands of hosts answered the spoofed victim at once — an amplifier. Broadcasts also serve recon: a broadcast ping sweep maps live hosts without addressing anyone. Broadcasts should never leave a subnet boundary — routers don't forward them, and the ones you hear define your segment."},
                            {"type": "text", "heading": "One-to-Many: Multicast", "body": "Multicast delivers to subscribed groups only — video distribution, routing protocol chatter (OSPF speaks to 224.0.0.5), and IGMP, the protocol clients use to join groups. Recon value: multicast chatter reveals infrastructure roles. Abuse: IGMP floods pressure multicast state in switches and routers. Well-run networks keep multicast scoped and documented — it should never surprise you."},
                            {"type": "text", "heading": "One-to-Closest: Anycast", "body": "Anycast gives one address to many servers; routing delivers each client to the nearest instance — how major DNS resolvers and CDNs absorb global load and DDoS traffic. For recon, anycast matters when you're mapping a target: hitting an anycast edge tells you nothing about the origin server behind it. Distinguishing CDN edge from origin is a real pentest skill (and origin discovery was Room 6's load-balancer lesson)."},
                            {"type": "practice", "command": "ping -c 2 -b 192.168.180.255 2>/dev/null || echo 'broadcast ping blocked (good)'", "instructions": "Try a directed broadcast ping on your own lab segment and see who answers — if a firewall blocks it, that's the modern default done right."}
                        ],
                        'questions': [
                            {
                                'order_index': 1,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'Normal one-to-one delivery, one sender to one recipient, is called what?',
                                'answer_hash': 'c95ae81b264312318b4d7cde85822a3a76f862c0f5686044e94fac392f7c75af',
                                'setup_script': None,
                            },
                            {
                                'order_index': 2,
                                'question_type': 'text',
                                'difficulty': 'easy',
                                'prompt': 'ARP requests and DHCP Discovery use one-to-all delivery on the local segment, called what?',
                                'answer_hash': 'e88199c423228a456677d367059b4f9b9fc769bae4a5c88aef9f7d0fcbe0726b',
                                'setup_script': None,
                            },
                            {
                                'order_index': 3,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which 1990s attack amplified a spoofed broadcast ping into a flood against a victim? (the attack name)',
                                'answer_hash': 'b3d7489cb114471f208b090bd4eb673ec0b0ab32eb1be8fddf82a0f4dd9bd71c|2cd5d21b2963257377c0333438b4562114a044a2c4e1468211881c85e8ae5c63',
                                'setup_script': None,
                            },
                            {
                                'order_index': 4,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which delivery method gives one address to many servers worldwide, routing each client to the nearest one? (one word)',
                                'answer_hash': '11c3776af93c97bdcda2ff7e52ea2822011d5b56e352ec30718e3d2fbb405fcf',
                                'setup_script': None,
                            },
                            {
                                'order_index': 5,
                                'question_type': 'text',
                                'difficulty': 'medium',
                                'prompt': 'Which protocol do clients use to join multicast groups? (the acronym)',
                                'answer_hash': 'b1577414de69f131f207b7695b91e76e6ddb35a877efb9edd7b7e7cbf6444bf2',
                                'setup_script': None,
                            },
                        ],
                    },
                ],
            },
        ],
    },
    {
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
    },
]


async def seed():
    async with AsyncSessionLocal() as db:
        for path_data in SEED_DATA:
            result = await db.execute(
                select(LearningPath).where(LearningPath.slug == path_data['slug'])
            )
            path = result.scalar_one_or_none()
            if path is None:
                path = LearningPath(
                    id=uuid.uuid4(),
                    slug=path_data['slug'],
                    title=path_data['title'],
                    description=path_data['description'],
                    icon=path_data['icon'],
                    order_index=path_data['order_index'],
                )
                db.add(path)
                await db.flush()
                print(f'Created path: {path.title}')
            else:
                path.title = path_data['title']
                path.description = path_data['description']
                path.icon = path_data['icon']
                path.order_index = path_data['order_index']
                print(f'Updated path: {path.title}')

            for room_data in path_data['rooms']:
                result = await db.execute(
                    select(Room)
                    .where(Room.path_id == path.id)
                    .where(Room.order_index == room_data['order_index'])
                )
                room = result.scalar_one_or_none()
                if room is None:
                    room = Room(
                        id=uuid.uuid4(),
                        path_id=path.id,
                        order_index=room_data['order_index'],
                        title=room_data['title'],
                        description=room_data['description'],
                    )
                    db.add(room)
                    await db.flush()
                    print(f'  Created room: {room.title}')
                else:
                    room.title = room_data['title']
                    room.description = room_data['description']
                    print(f'  Updated room: {room.title}')

                for lesson_data in room_data['lessons']:
                    result = await db.execute(
                        select(Lesson)
                        .where(Lesson.room_id == room.id)
                        .where(Lesson.order_index == lesson_data['order_index'])
                    )
                    lesson = result.scalar_one_or_none()
                    if lesson is None:
                        lesson = Lesson(
                            id=uuid.uuid4(),
                            room_id=room.id,
                            order_index=lesson_data['order_index'],
                            title=lesson_data['title'],
                            blocks=lesson_data['blocks'],
                        )
                        db.add(lesson)
                        await db.flush()
                        print(f'    Created lesson: {lesson.title}')
                    else:
                        lesson.title = lesson_data['title']
                        lesson.blocks = lesson_data['blocks']
                        print(f'    Updated lesson: {lesson.title}')

                    for q_data in lesson_data.get('questions', []):
                        result = await db.execute(
                            select(LessonQuestion)
                            .where(LessonQuestion.lesson_id == lesson.id)
                            .where(LessonQuestion.order_index == q_data['order_index'])
                        )
                        question = result.scalar_one_or_none()
                        if question is None:
                            question = LessonQuestion(
                                id=uuid.uuid4(),
                                lesson_id=lesson.id,
                                order_index=q_data['order_index'],
                                question_type=QuestionType(q_data['question_type']),
                                difficulty=QuestionDifficulty(q_data['difficulty']),
                                prompt=q_data['prompt'],
                                answer_hash=_resolve_answer_hash(q_data),
                                setup_script=q_data.get('setup_script'),
                            )
                            db.add(question)
                            print(f'      Created question #{q_data["order_index"]}')
                        else:
                            question.prompt = q_data['prompt']
                            question.difficulty = QuestionDifficulty(q_data['difficulty'])
                            question.answer_hash = _resolve_answer_hash(q_data)
                            question.setup_script = q_data.get('setup_script')
                            print(f'      Updated question #{q_data["order_index"]}')

        await db.commit()
        print('\nLearning paths seeded successfully')


if __name__ == '__main__':
    asyncio.run(seed())