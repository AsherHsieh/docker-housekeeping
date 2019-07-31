# openSUSE Leap 15 with cron
FROM opensuse/leap:15

# Install cron
RUN zypper -n install vim cron

# install ansible python sshpass openssh
RUN zypper -n install python
RUN zypper -n install ansible
RUN zypper -n install sshpass
RUN zypper -n install openssh

# copy all files to ailab folder
COPY ailab/ /ailab/

# grant execution rights
RUN chmod 755 /ailab/docker_purge.sh /ailab/sendmail.py /ailab/sendpurgemail.py
RUN chmod 644 /ailab/cron-ansible

# set up crontab
RUN crontab /ailab/cron-ansible
CMD [ "cron", "-n" ]

# set up crontab
RUN mkdir /ailab/log

WORKDIR /ailab
