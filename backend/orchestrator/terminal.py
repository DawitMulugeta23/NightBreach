import base64
import docker

_docker_client = docker.from_env()


def get_docker_client():
    return _docker_client


def create_exec_socket(container_id: str, username: str = "player"):
    """
    Opens an interactive bash session inside the container as `username`,
    with a colored prompt and colorized ls output.

    Uses --color=always for ls/grep (auto won't fire when the shell is
    piped through docker exec on some kernels).
    """
    # Colored prompt: green username, white @rohactf, blue cwd
    prompt = (
        f"\\[\\e[1;32m\\]{username}\\[\\e[0m\\]"
        f"@"
        f"\\[\\e[1;37m\\]mDe\\[\\e[0m\\]"
        f":"
        f"\\[\\e[1;34m\\]\\w\\[\\e[0m\\]"
        f"\\$ "
    )

    # Full GNU LS_COLORS mapping
    ls_colors = (
        "rs=0:di=01;34:ln=01;36:mh=00:pi=40;33:so=01;35:do=01;35:"
        "bd=40;33;01:cd=40;33;01:or=40;31;01:mi=00:"
        "su=37;41:sg=30;43:ca=00:tw=30;42:ow=34;42:st=37;44:"
        "ex=01;32:"
        "*.tar=01;31:*.tgz=01;31:*.arc=01;31:*.arj=01;31:*.taz=01;31:"
        "*.lha=01;31:*.lz4=01;31:*.lzh=01;31:*.lzma=01;31:*.tlz=01;31:"
        "*.txz=01;31:*.tzo=01;31:*.t7z=01;31:*.zip=01;31:*.z=01;31:"
        "*.dz=01;31:*.gz=01;31:*.lrz=01;31:*.lz=01;31:*.lzo=01;31:"
        "*.xz=01;31:*.zst=01;31:*.tzst=01;31:*.bz2=01;31:*.bz=01;31:"
        "*.tbz=01;31:*.tbz2=01;31:*.tz=01;31:*.deb=01;31:*.rpm=01;31:"
        "*.jar=01;31:*.war=01;31:*.ear=01;31:*.sar=01;31:*.rar=01;31:"
        "*.alz=01;31:*.ace=01;31:*.zoo=01;31:*.cpio=01;31:*.7z=01;31:"
        "*.rz=01;31:*.cab=01;31:"
        "*.jpg=01;35:*.jpeg=01;35:*.mjpg=01;35:*.mjpeg=01;35:"
        "*.gif=01;35:*.bmp=01;35:*.pbm=01;35:*.pgm=01;35:*.ppm=01;35:"
        "*.tga=01;35:*.xbm=01;35:*.xpm=01;35:*.tif=01;35:*.tiff=01;35:"
        "*.png=01;35:*.svg=01;35:*.svgz=01;35:*.mng=01;35:*.pcx=01;35:"
        "*.mov=01;35:*.mpg=01;35:*.mpeg=01;35:*.m2v=01;35:*.mkv=01;35:"
        "*.webm=01;35:*.ogm=01;35:*.mp4=01;35:*.m4v=01;35:*.mp4v=01;35:"
        "*.vob=01;35:*.qt=01;35:*.nuv=01;35:*.wmv=01;35:*.asf=01;35:"
        "*.rm=01;35:*.rmvb=01;35:*.flc=01;35:*.avi=01;35:*.fli=01;35:"
        "*.flv=01;35:*.gl=01;35:*.dl=01;35:*.xcf=01;35:*.xwd=01;35:"
        "*.yuv=01;35:*.cgm=01;35:*.emf=01;35:*.ogv=01;35:*.ogx=01;35:"
        "*.aac=00;36:*.au=00;36:*.flac=00;36:*.m4a=00;36:*.mid=00;36:"
        "*.midi=00;36:*.mka=00;36:*.mp3=00;36:*.mpc=00;36:*.ogg=00;36:"
        "*.ra=00;36:*.wav=00;36:*.oga=00;36:*.opus=00;36:*.spx=00;36:"
        "*.xspf=00;36:"
        "*.py=00;33:*.js=00;33:*.json=00;33:*.html=00;33:*.htm=00;33:"
        "*.css=00;33:*.md=00;33:*.yml=00;33:*.yaml=00;33:"
        "*.conf=00;36:*.log=00;35:*.txt=00;33"
    )

    rcfile = "\n".join([
        f'export PS1="{prompt}"',
        f'export LS_COLORS="{ls_colors}"',
        'export CLICOLOR=1',
        'export CLICOLOR_FORCE=1',
        'export TERM=xterm-256color',
        'export COLORTERM=truecolor',
        "alias ls='ls --color=always'",
        "alias la='ls -A --color=always'",
        "alias ll='ls -alF --color=always'",
        "alias l='ls -CF --color=always'",
        "alias grep='grep --color=always'",
        "alias fgrep='fgrep --color=always'",
        "alias egrep='egrep --color=always'",
        "alias tree='tree -C'",
        "",
    ])

    rcpath = f"/tmp/.roha_rc_{username}"

    # Base64-write the rcfile (safe from shell escaping)
    b64 = base64.b64encode(rcfile.encode()).decode()
    write_cmd = f"echo {b64} | base64 -d > {rcpath} && chmod 644 {rcpath}"
    write_id = _docker_client.api.exec_create(
        container_id,
        ["/bin/bash", "-c", write_cmd],
        user="root",
    )["Id"]
    _docker_client.api.exec_start(write_id, tty=False)

    # Launch bash — pass LS_COLORS/TERM directly through exec env too,
    # so even if the rcfile is somehow ignored, colors still work.
    exec_id = _docker_client.api.exec_create(
        container_id,
        [
            "/bin/bash",
            "--noprofile",
            "--rcfile", rcpath,
            "-i",
        ],
        environment=[
            f"HOME=/home/{username}",
            f"USER={username}",
            f"LOGNAME={username}",
            "TERM=xterm-256color",
            "COLORTERM=truecolor",
            f"LS_COLORS={ls_colors}",
        ],
        workdir=f"/home/{username}",
        user=username,
        stdin=True,
        tty=True,
        stdout=True,
        stderr=True,
    )["Id"]

    sock = _docker_client.api.exec_start(exec_id, socket=True, tty=True)
    raw_sock = sock._sock if hasattr(sock, "_sock") else sock
    raw_sock.setblocking(True)
    return raw_sock
