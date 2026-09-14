FROM ubuntu:24.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server \
    sudo \
    vim \
    nano \
    curl \
    wget \
    net-tools \
    iputils-ping \
    tree \
    less \
    man-db \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /var/run/sshd

# Temporary fixed credentials for V1 plumbing test only.
# MUST be replaced with per-session random passwords or SSH key injection
# before any real user touches this.
RUN useradd -m -s /bin/bash player \
    && usermod -aG sudo player

RUN sed -i 's/#PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config \
    && sed -i 's/#PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]
