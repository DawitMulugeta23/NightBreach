# Pin to a digest once the build host has a reliable connection.
FROM alpine:latest
LABEL org.opencontainers.image.title="nightbreach/linux-permissions-target" \
      org.opencontainers.image.version="1.0" \
      nightbreach.role="TARGET" \
      nightbreach.vulnerability="linux-permissions-001"

RUN apk add --no-cache openssh-server bash \
 && mkdir -p /run/sshd /srv/backups \
 && addgroup ops \
 && adduser -D -s /bin/bash student \
 && adduser -D -s /bin/bash -G ops webadmin \
 && echo 'student:Student#2024' | chpasswd \
 && echo "webadmin:$(head -c 24 /dev/urandom | base64)" | chpasswd \
 && ssh-keygen -q -t ed25519 -N '' -f /etc/ssh/ssh_host_ed25519_key

COPY files/sshd_config /etc/ssh/sshd_config
COPY files/motd /etc/motd
COPY files/notes.txt files/payroll.csv files/db-backup.sql /srv/backups/
COPY files/nb-set-flag /usr/local/sbin/nb-set-flag

# Intentional misconfiguration (confined to this container):
#   db-backup.sql is world-readable although it holds credentials/secrets.
# Correctly protected decoy: payroll.csv (root:ops 0640).
RUN chmod 0755 /srv/backups /usr/local/sbin \
 && chmod 0700 /usr/local/sbin/nb-set-flag \
 && chown root:root /srv/backups/db-backup.sql /srv/backups/notes.txt \
 && chmod 0644 /srv/backups/db-backup.sql /srv/backups/notes.txt \
 && chown root:ops /srv/backups/payroll.csv \
 && chmod 0640 /srv/backups/payroll.csv

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D", "-e"]
