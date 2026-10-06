"""Content blocks for the lesson 'Linux File Permissions'. Pure data, no app imports."""


def h(text):
    return ("HEADING", {"text": text})


def t(text):
    return ("TEXT", {"text": text})


def out(text):
    return ("TERMINAL_OUTPUT", {"text": text})


def callout(kind, title, text):
    return ("CALLOUT", {"type": kind, "title": title, "text": text})


def code(source, breakdown, language="bash"):
    return ("CODE", {
        "language": language,
        "code": source,
        "breakdown": [{"part": part, "meaning": meaning} for part, meaning in breakdown],
    })


BLOCKS = [
    h("Who is allowed to do what?"),
    t("Every file on a Linux system has an owner, a group and a set of permissions. "
      "Permissions are split into three classes: the owner (user), the group, and everyone "
      "else (others). Each class can be given read (r), write (w) and execute (x) rights."),

    h("Reading permissions with ls -l"),
    code("ls -l notes.txt", [
        ("ls", "Lists directory contents."),
        ("-l", "Long format: one line per file showing the type and permissions, link count, "
               "owner, group, size in bytes, modification time and name."),
        ("notes.txt", "The file to describe. Without it, ls lists the current directory."),
    ]),
    out("-rw-r--r-- 1 alice staff 220 Oct  6 09:12 notes.txt"),
    t("Read the line from left to right:\n"
      "-  first character is the type: - file, d directory, l symbolic link\n"
      "rw-  permissions of the owner: read and write, no execute\n"
      "r--  permissions of the group: read only\n"
      "r--  permissions of everyone else: read only\n"
      "1  number of hard links      alice  owner      staff  group\n"
      "220  size in bytes      Oct 6 09:12  last modified      notes.txt  name"),
    code("ls -lah /srv/backups", [
        ("ls", "Lists directory contents."),
        ("-l", "Long format, as above."),
        ("-a", "All entries, including hidden ones whose names start with a dot (. and ..)."),
        ("-h", "Human-readable sizes such as 4.0K or 1.2M (used together with -l)."),
        ("-lah", "Single-letter options can be combined: -lah is the same as -l -a -h."),
        ("/srv/backups", "The directory to list."),
    ]),

    h("Permissions as numbers"),
    t("Each right has a value: read = 4, write = 2, execute = 1. Add the ones you want for "
      "each class.\n"
      "rwx = 4+2+1 = 7      rw- = 4+2 = 6      r-- = 4      --- = 0\n"
      "So 640 means: owner rw-, group r--, others ---."),
    code("stat -c '%a %U:%G %n' notes.txt", [
        ("stat", "Shows detailed status information about a file."),
        ("-c", "Use a custom output format instead of the default report."),
        ("'%a %U:%G %n'", "The format: %a permissions in octal, %U owner name, %G group name, "
                          "%n file name. The quotes keep it together as one argument."),
        ("notes.txt", "The file to inspect."),
    ]),
    out("644 alice:staff notes.txt"),

    h("Changing permissions: chmod"),
    code("chmod 640 report.txt", [
        ("chmod", "Changes a file's mode, which means its permissions."),
        ("640", "Three octal digits for owner, group and others: 6 = rw-, 4 = r--, 0 = ---."),
        ("report.txt", "The file to change."),
    ]),
    code("chmod o-r db-backup.sql\nchmod u+x backup.sh", [
        ("o-r", "o = others, - = remove, r = read. Removes read access from everyone else."),
        ("u+x", "u = the owner, + = add, x = execute. Lets the owner run the file."),
        ("who letters", "u owner, g group, o others, a all three."),
        ("operators", "+ adds a right, - removes it, = sets exactly the rights you list."),
    ]),
    code("chmod -R 750 project/", [
        ("-R", "Recursive: applies the change to the directory and everything inside it."),
        ("750", "Owner rwx, group r-x, others none. On a directory, x means you may enter it."),
        ("project/", "The directory to change."),
    ]),

    h("Changing the owner: chown"),
    code("chown alice:staff report.txt", [
        ("chown", "Changes the owner and/or group of a file. Normally only root may do this, "
                  "so it is usually run with sudo."),
        ("alice:staff", "New owner, a colon, then the new group. 'alice' alone changes only "
                        "the owner; ':staff' alone changes only the group."),
        ("report.txt", "The file to change."),
    ]),

    h("Default permissions: umask"),
    code("umask\numask 027", [
        ("umask", "With no argument, prints the current mask."),
        ("umask 027", "Sets the mask for this shell. The digits are rights taken away from "
                      "new files: owner 0 (nothing), group 2 (write), others 7 (everything)."),
        ("result", "New files start from 666 and directories from 777, so with 027 they "
                   "become 640 and 750."),
    ]),
    callout("important", "Cybersecurity connection",
            "Overly permissive files are one of the most common real-world findings. A backup, "
            "a configuration file or a key that everyone can read turns any low-privilege "
            "account into a source of secrets."),

    h("Lab: find the exposed file"),
    t("You get two machines on a private network: an attack machine, which is the terminal "
      "you control, and a target server. Find a file on the target whose permissions expose "
      "sensitive data and recover the flag stored in it."),
    t("1. Start the lab from the lab panel and open the terminal on the attack machine.\n"
      "2. Find the target on the lab network shown in the panel.\n"
      "3. Log in to the target over SSH as student with the password Student#2024.\n"
      "4. Look where backups are kept and compare file permissions.\n"
      "5. Submit the flag you recover. It looks like NB{...}."),

    h("Commands you will use in the lab"),
    code("nmap -sn <subnet>", [
        ("nmap", "A network scanner that discovers hosts and open ports."),
        ("-sn", "Ping scan only: lists which hosts are up and does not scan their ports."),
        ("<subnet>", "The lab network from the panel, written like 10.200.1.0/24. The /24 "
                     "means all 256 addresses that share the first three numbers."),
    ]),
    code("nmap -p 22 <target-ip>", [
        ("-p 22", "Scan only port 22, the default port of SSH. Use -p- for all ports."),
        ("<target-ip>", "An address you found with the scan above."),
    ]),
    code("ssh student@<target-ip>", [
        ("ssh", "Secure Shell client: opens a shell on another machine over the network."),
        ("student@<target-ip>", "User name, an @ sign, then the host to connect to."),
        ("-p 2222 (optional)", "Connect to a port other than 22."),
        ("-i key (optional)", "Log in with a private key file instead of a password."),
    ]),
    code("ls -l /srv/backups", [
        ("ls -l", "Long listing, as above: look at the permission column of every file."),
        ("/srv/backups", "The directory that holds the backups on the target."),
    ]),
    code("cat /srv/backups/db-backup.sql", [
        ("cat", "Prints the contents of a file to the terminal."),
        ("/srv/backups/db-backup.sql", "The file to read. 'Permission denied' means your "
                                       "user has no read right on it."),
        ("-n (optional)", "Number the output lines."),
    ]),
    callout("tip", "Hint",
            "Compare the permission strings in the listing. A file that others can read is "
            "readable by every account on the system, including yours."),
    callout("warning", "The lab is disposable",
            "The attack machine can only reach the target. If you break something, reset the lab."),
]
