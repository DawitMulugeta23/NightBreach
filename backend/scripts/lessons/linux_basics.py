"""Content blocks for the six lessons of 'Linux Command Line Basics'.
Pure data, no app imports. Every command explains each part and option."""
from .linux_file_permissions import callout, code, h, out, t

CONTENT = {
    "linux-and-the-shell": [
        h("What is Linux?"),
        t("Linux is an operating system widely used on servers, security appliances, cloud "
          "systems, development machines, and security laboratories. In cybersecurity, Linux is "
          "important because many security tools and servers are operated from the command line."),
        h("The Terminal"),
        t("The terminal provides a text interface through which you interact with the operating "
          "system. Instead of clicking graphical controls, you type commands and receive text output."),
        code("student@attacker:~$", [
            ("student", "Your user name."),
            ("@", "Separates the user name from the machine name."),
            ("attacker", "The name of the machine you are working on."),
            (":~", "Your current directory. ~ is a shortcut for your home directory."),
            ("$", "You are a normal user and the shell is waiting for a command. A # here would "
                  "mean you are root, the administrator."),
        ], language="text"),
        h("The Shell"),
        t("A shell interprets commands entered in the terminal. Bash is one of the most common "
          "shells on Linux systems."),
        code("echo Hello, Linux!", [
            ("echo", "Prints its arguments to the terminal."),
            ("Hello, Linux!", "The shell splits the line at spaces, so echo receives two "
                              "arguments, Hello, and Linux!, and prints them with one space between."),
            ('"..." (quotes)', 'Keep text together exactly as typed, for example echo "a   b" keeps the spaces.'),
            ("-n (optional)", "Do not print the newline at the end."),
            ("-e (optional)", "Interpret escape sequences such as \\n (new line)."),
        ]),
        out("Hello, Linux!"),
        callout("important", "Cybersecurity connection",
                "Security analysts and penetration testers frequently automate tasks through shell "
                "commands and shell scripts."),
    ],

    "navigating-the-filesystem": [
        h("The Linux Filesystem"),
        t("Linux organizes files and directories in a hierarchical filesystem. The top of this "
          "hierarchy is represented by the root directory, written as /."),
        t("Directories you will meet often:\n"
          "/home holds the personal files of each user.\n"
          "/etc holds system configuration files.\n"
          "/var holds data that changes, such as logs.\n"
          "/tmp holds temporary files.\n"
          "/usr holds installed programs."),
        h("Where Am I?"),
        t("The pwd command prints the current working directory."),
        code("pwd", [
            ("pwd", "Print Working Directory: shows the full path of the directory you are in."),
            ("-L (optional)", "Show the path as you typed it, including symbolic links. This is the default."),
            ("-P (optional)", "Show the real physical path with symbolic links resolved."),
        ]),
        out("/home/student"),
        h("Listing a Directory"),
        code("ls", [
            ("ls", "Lists the names of the files and directories in the current directory."),
            ("-l (optional)", "Long format with permissions, owner, size and date."),
            ("-a (optional)", "Include hidden entries, whose names start with a dot."),
            ("-h (optional)", "With -l, print sizes like 4.0K or 1.2M instead of bytes."),
            ("-R (optional)", "Recursive: also list the contents of every subdirectory."),
            ("/path (optional)", "List that directory instead of the current one, for example ls /tmp."),
        ]),
        t("The ls command displays files and directories inside the current directory."),
        h("Changing Directories"),
        code("cd /tmp\npwd", [
            ("cd", "Change Directory: moves your shell to another directory."),
            ("/tmp", "The destination, written as an absolute path starting at /."),
            ("pwd", "Confirms where you are now."),
            ("cd (alone)", "Goes back to your home directory."),
            ("cd -", "Goes back to the previous directory."),
            ("cd ..", "Goes up one level, to the parent directory."),
        ]),
        out("/tmp"),
        callout("warning", "Common mistake",
                "Remember that cd changes your current directory, while ls only displays directory contents."),
    ],

    "files-and-directories": [
        h("Creating a Directory"),
        code("mkdir linux-lab", [
            ("mkdir", "Make Directory: creates a new, empty directory."),
            ("linux-lab", "The name of the new directory, created inside the current directory."),
            ("-p (optional)", "Create missing parent directories too, and do not complain if it "
                              "already exists, for example mkdir -p a/b/c."),
            ("-v (optional)", "Verbose: print a line for every directory created."),
        ]),
        t("mkdir creates a new directory. After creating linux-lab, you can enter it with cd."),
        code("cd linux-lab", [
            ("cd", "Change Directory."),
            ("linux-lab", "A relative path: the directory with this name inside the current one."),
        ]),
        h("Creating a File"),
        code("touch notes.txt", [
            ("touch", "Creates an empty file if it does not exist. If it exists, only its "
                      "modification time is updated."),
            ("notes.txt", "The name of the file."),
            ("-c (optional)", "Do not create the file if it does not already exist."),
        ]),
        t("touch can create an empty file when the file does not already exist."),
        h("Reading a File"),
        code("cat notes.txt", [
            ("cat", "Prints the contents of a file to the terminal."),
            ("notes.txt", "The file to read. You can give several files and they are printed one after another."),
            ("-n (optional)", "Number the output lines."),
        ]),
        t("notes.txt is still empty, so cat prints nothing. Put some text into it first:"),
        code('echo "first note" > notes.txt\ncat notes.txt', [
            ('echo "first note"', "Produces the text first note."),
            (">", "Redirects the output into a file instead of the screen. It replaces the file's "
                  "content. Use >> to add to the end instead."),
            ("notes.txt", "The file that receives the text."),
            ("cat notes.txt", "Shows what is now stored in the file."),
        ]),
        out("first note"),
        h("Copying and Moving"),
        code("cp notes.txt backup.txt\nmv backup.txt archive.txt", [
            ("cp notes.txt backup.txt", "Copy: makes a second file with the same content. The "
                                        "original stays. The first name is the source, the second the destination."),
            ("mv backup.txt archive.txt", "Move: moves a file, or renames it when the destination "
                                          "is in the same directory, as here. The old name disappears."),
            ("-i (optional)", "Ask before overwriting an existing file. Works with cp and mv."),
            ("-r (optional)", "With cp, copy directories and everything inside them."),
        ]),
        callout("important", "Security connection",
                "Security investigations frequently involve creating evidence copies, inspecting "
                "files, and moving artifacts into analysis directories."),
    ],

    "absolute-and-relative-paths": [
        h("Absolute Paths"),
        t("An absolute path starts from the filesystem root. For example, /home/student/notes.txt "
          "identifies a specific location from the root of the filesystem."),
        code("cat /home/student/notes.txt", [
            ("cat", "Prints the contents of a file."),
            ("/home/student/notes.txt", "An absolute path. It starts with /, so it means the "
                                        "same file no matter which directory you are in."),
            ("/", "The root directory."),
            ("home", "A directory inside /."),
            ("student", "A directory inside home, here the home directory of the user student."),
            ("notes.txt", "The file inside it."),
        ]),
        h("Relative Paths"),
        t("A relative path is interpreted from the current working directory."),
        code("cat notes.txt", [
            ("cat", "Prints the contents of a file."),
            ("notes.txt", "A relative path: it does not start with /, so Linux looks for it in "
                          "the current directory. If it is not there you get No such file or directory."),
        ]),
        h("Parent Directory"),
        t("The special path .. represents the parent directory. A single dot, ., represents the "
          "current directory."),
        code("cd ..\npwd", [
            ("cd ..", "Moves up one level, to the parent directory."),
            ("pwd", "Prints where you are now."),
            (". (single dot)", "The current directory, for example ./script.sh runs a script in it."),
            ("~", "Your home directory. cd ~ and cd with no argument both take you there."),
        ]),
        t("If you start in /home/student/linux-lab, pwd now prints /home/student."),
        callout("tip", "Remember",
                "Absolute paths begin from /. Relative paths begin from your current working directory."),
    ],

    "reading-command-help": [
        h("Why Documentation Matters"),
        t("Linux contains a large number of commands and options. Cybersecurity practitioners "
          "should learn how to read documentation instead of relying entirely on memorization."),
        t("Most options come in two forms: a short form with one dash and one letter, and a long "
          "form with two dashes and a word. ls -a and ls --all do exactly the same thing."),
        h("The --help Option"),
        code("ls --help", [
            ("ls", "The command you want help with."),
            ("--help", "A long option that makes the command print a short usage summary and its "
                       "list of options, then exit without doing anything else."),
        ]),
        t("Many commands provide a short usage summary through the --help option."),
        h("Manual Pages"),
        code("man ls", [
            ("man", "Opens the manual page of a command."),
            ("ls", "The command you want to read about."),
            ("Space / b", "Scroll one page down / one page back."),
            ("/text then n", "Search for text, then jump to the next match."),
            ("q", "Quit the manual."),
            ("man -k word (optional)", "Search all manual pages for a keyword when you do not know the command name."),
        ]),
        t("The man command opens the manual page for a command. Manual pages are one of the most "
          "useful references available on a Linux system."),
        code("ls [OPTION]... [FILE]...", [
            ("[ ]", "Square brackets mean the part is optional."),
            ("OPTION", "Replace it with a real option such as -l."),
            ("FILE", "Replace it with a file or directory name."),
            ("...", "The part before it may be repeated."),
        ], language="text"),
        t("The line above is the kind of SYNOPSIS you see at the top of a manual page. Read it to "
          "learn which parts of a command you may leave out."),
        callout("important", "Cybersecurity habit",
                "Before using an unfamiliar command in a real environment, understand what it "
                "does and what its options change."),
    ],

    "command-line-workflow": [
        h("A Practical Workflow"),
        t("Effective command-line work is usually a sequence of small, verifiable operations. First "
          "determine where you are, inspect the directory, create or select the required files, "
          "and verify the result."),
        code("pwd\nls\nmkdir lab\ncd lab\ntouch evidence.txt\nls", [
            ("pwd", "Where am I?"),
            ("ls", "What is here? Prints nothing if the directory is empty."),
            ("mkdir lab", "Create a directory named lab."),
            ("cd lab", "Enter it."),
            ("touch evidence.txt", "Create an empty file inside lab."),
            ("ls", "Verify: the new file should now be listed."),
        ]),
        out("/home/student\nevidence.txt"),
        t("The first ls printed nothing because the directory was empty, and the last ls shows "
          "evidence.txt, which proves the file was created inside lab. If your directory already "
          "contained files, the first ls lists them."),
        h("Verify Your Work"),
        t("Verification is an important security habit. Do not assume a command succeeded simply "
          "because it was entered. Inspect the resulting state."),
        code("pwd\nls -la", [
            ("pwd", "Confirms which directory you are in."),
            ("ls -la", "A long listing that includes hidden entries."),
            ("-l", "Long format: permissions, owner, group, size, date and name."),
            ("-a", "All entries, including . (this directory) and .. (its parent)."),
            ("-la", "Short options can be combined: -la is the same as -l -a."),
        ]),
        out("/home/student/lab\n"
            "total 8\n"
            "drwxr-xr-x 2 student student 4096 Oct  6 10:02 .\n"
            "drwxr-xr-x 3 student student 4096 Oct  6 10:02 ..\n"
            "-rw-r--r-- 1 student student    0 Oct  6 10:02 evidence.txt"),
        t("evidence.txt has size 0 because it is empty. The d at the start of the first two lines "
          "marks directories, the - at the start of the last line marks a regular file."),
        callout("important", "Security mindset",
                "A strong Linux workflow is deliberate: execute, observe, verify, and only then continue."),
    ],
}
