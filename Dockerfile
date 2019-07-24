# openSUSE Leap 15 with cron
FROM opensuse/leap:15

# Install cron
RUN zypper -n install vim cron

# install ansible python sshpass openssh
RUN zypper -n install python
RUN zypper -n install ansible
RUN zypper -n install sshpass
RUN zypper -n install openssh

COPY ailab/ /ailab/
WORKDIR /ailab
