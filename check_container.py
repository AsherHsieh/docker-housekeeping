#!/usr/bin/python
import os
import mmap
import ast
import smtplib
import socket

# Import the email modules we'll need
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
SendMail = False

sender = "python_check@gmail.com"
receiver = "username@gmail.com"

# list the name of all running container
myCmd = 'docker ps --format {{.Names}} > docker_ps_Name.txt'
os.system(myCmd)

# save the running container to a file
NameData = open('docker_ps_Name.txt', "r")
lines = NameData.readlines()
NameData.close()

# open the container_registry
f = open('/home/developer/ServerMgt/container_registry')
s = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
f.close()

# check CompareDockerNameRecord.txt is existed or not
cp_dict = {}
mail_dict = {}
if os.path.exists('/tmp/CompareDockerNameRecord.txt') == False:
    newfile = open("/tmp/CompareDockerNameRecord.txt","w+")
    FirstTime = True
else:
    newfile = open("/tmp/CompareDockerNameRecord.txt","r+")
    cp_dict = ast.literal_eval(newfile.read()) # read file as dictionary format
    mail_dict = cp_dict.copy()
    FirstTime = False

# log remove container 
log_dict = {}
LogRemove = False

# compare container name
for i in range(len(lines)):
    if s.find(lines[i].strip('\n')) == -1: # check if register
        #print(lines[i])
        if lines[i].startswith("project") == False: # check if is project
            #print(lines[i])
            if FirstTime == True: # check if record file is first time created
                #print(lines[i])
                cp_dict[lines[i].strip('\n')] = 1
                mail_dict[lines[i].strip('\n')] = 1
                SendMail = True # send mail function
            else: # the record file has existed
                if lines[i].strip('\n') in cp_dict.keys(): #the container name is already in file
                    if int(cp_dict[lines[i].strip('\n')]) < 3:
                        cp_dict[lines[i].strip('\n')] = int(cp_dict[lines[i].strip('\n')]) + 1
                        mail_dict[lines[i].strip('\n')] = int(mail_dict[lines[i].strip('\n')]) + 1
                        SendMail = True #send mail function
                        if int(cp_dict[lines[i].strip('\n')]) == 3:
                            mail_dict[lines[i].strip('\n')] = '<font color="red">3</font>'
                    else:
                        #os.system('docker stop ' + lines[i].strip('\n')) # stop the docker container
                        #os.system('docker rm ' + lines[i].strip('\n'))
                        LogRemove = True
                        log_dict[lines[i].strip('\n')] = 'deleted'
                else: #the container name first time show up in file
                    cp_dict.update({lines[i].strip('\n'): 1})
                    mail_dict.update({lines[i].strip('\n'): 1})
                    SendMail = True #send mail function

# remove docker_ps_Name.txt
os.system('rm -f docker_ps_Name.txt')

# Record the container which has been removed
if LogRemove:
    logfile = open("/tmp/DockerDeleteRecord.txt","w+a")
    logfile.write(str(log_dict))
    logfile.close()

if SendMail:
    msg = MIMEMultipart('alternative')
    fixedtemplate = 'There is some container with the wrong format of the name.<br><font color="red">If you are using these containers, please register the correct name of the container to "container_registry" file or modify the name of the running container.</font><br>We will inform this message <font color="red" size="20">three times</font> before we stop and remove these containers.<br>Please check on <font color="red" size="20">' + socket.gethostname() + '</font> (container_name: counting_times) as below:<br>'
    content = MIMEText(fixedtemplate + str(mail_dict), 'html')
    # the detail of mail
    msg['Subject'] = '[Important Information] There is some container with the wrong format of the name.'
    msg['From'] = sender
    msg['To'] = receiver
    msg.attach(content)
    # Send the message via our own SMTP server, but don't include the envelope header.
    send = smtplib.SMTP('smtp.google.com')
    send.sendmail(sender, receiver, msg.as_string())
    send.quit()

#print cp_dict
newfile.seek(0)
newfile.write(str(cp_dict))
newfile.truncate()
newfile.close()
