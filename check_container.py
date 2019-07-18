#!/usr/bin/python
import os
import mmap
import ast
import smtplib
import socket

# Import the email modules we'll need
from email.mime.text import MIMEText
SendMail = False

# list the name of all running container
myCmd = 'docker ps --format {{.Names}} > docker_ps_Name.txt'
os.system(myCmd)

# save the running container to a file
NameData = open('docker_ps_Name.txt', "r")
lines = NameData.readlines()
NameData.close()

# open the container_registry
f = open('container_registry')
s = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
f.close()

# check CompareDockerNameRecord.txt is existed or not
cp_dict = {}
if os.path.exists('CompareDockerNameRecord.txt') == False:
    newfile = open("CompareDockerNameRecord.txt","w+")
    FirstTime = True
else:
    newfile = open("CompareDockerNameRecord.txt","r+")
    cp_dict = ast.literal_eval(newfile.read()) # read file as dictionary format
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
                SendMail = True # send mail function
            else: # the record file has existed
                if lines[i].strip('\n') in cp_dict.keys(): #the container name is already in file
                    if int(cp_dict[lines[i].strip('\n')]) < 3:
                        cp_dict[lines[i].strip('\n')] = int(cp_dict[lines[i].strip('\n')]) + 1
                        SendMail = True #send mail function
                    else:
                        #os.system('docker stop ' + lines[i].strip('\n')) # stop the docker container
                        #os.system('docker rm ' + lines[i].strip('\n'))
                        LogRemove = True
                        log_dict[lines[i].strip('\n')] = 'deleted'
                else: #the container name first time show up in file
                    cp_dict.update({lines[i].strip('\n'): 1})
                    SendMail = True #send mail function

# Record the container which has been removed
if LogRemove:
    logfile = open("DockerDeleteRecord.txt","w+a")
    logfile.write(str(log_dict))
    logfile.close()

if SendMail:
    msg = MIMEText("There is some container with the wrong format of the name.\nIf you are using these containers, please register the correct name of the container to 'container_registry' file or modify the name of the running container.\nWe will inform this message three times before we stop and remove these containers.\nPlease check on " + socket.gethostname() + " (container_name: counting_times) as below:\n" + str(cp_dict))
    # the detail of mail
    msg['Subject'] = '[Important Information] There is some container with the wrong format of the name.'
    msg['From'] = "python_check@gmail.com"
    msg['To'] = "username@gmail.com"
    # Send the message via our own SMTP server, but don't include the envelope header.
    send = smtplib.SMTP('smtp.google.com')
    send.sendmail("python_check@gmail.com", ["username@gmail.com"], msg.as_string())
    send.quit()

#print cp_dict
newfile.seek(0)
newfile.write(str(cp_dict))
newfile.truncate()
newfile.close()
