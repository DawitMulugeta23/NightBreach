FROM debian:bookworm-slim
LABEL org.opencontainers.image.title="nightbreach/attacker" \
      org.opencontainers.image.version="1.0" \
      nightbreach.role="ATTACKER"
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      bash ca-certificates curl file iproute2 iputils-ping less nano \
      netcat-openbsd nmap openssh-client procps python3-minimal sshpass \
      tree vim-tiny \
 && rm -rf /var/lib/apt/lists/* \
 && useradd -m -u 1000 -s /bin/bash learner
COPY --chown=learner:learner bashrc /home/learner/.bashrc
USER learner
WORKDIR /home/learner
CMD ["sleep", "infinity"]
