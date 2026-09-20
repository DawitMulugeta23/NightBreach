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
                        'order_index': 3,
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
                        'order_index': 4,
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
                        'order_index': 5,
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
                        'order_index': 6,
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
                        'order_index': 7,
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
                        'order_index': 8,
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
                        'order_index': 9,
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
                        'order_index': 10,
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
                        'order_index': 8,
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
                'description': 'Advanced permissions, text processing, and troubleshooting.',
                'lessons': [
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
        'title': 'Reconnaissance',
        'description': 'Discovering hosts, open ports, and running services before any attack.',
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
],
    },
    {
        'slug': 'web-app-hacking',
        'title': 'Web Application Hacking',
        'description': 'Analyze and exploit OWASP Top 10 web vulnerabilities and tackle complex labs.',
        'icon': '/webapppentest.jpg',
        'order_index': 6,
        'rooms': [
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