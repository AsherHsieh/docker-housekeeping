#!/usr/bin/python
import os
import subprocess
import ast
import smtplib
import socket
from datetime import *

# Import the email modules we'll need
from email.mime.text import MIMEText
SendMail = False

# list the name of all running container
myCmd = "docker ps -a | grep -i 'exited' | awk {'print $1'} > docker_exited_id.txt"
os.system(myCmd)

# read the id
IDData = open('docker_exited_id.txt', "r")
lines = IDData.readlines()
IDData.close()

# save the compare inforamtion
cp_dict = {}
if os.path.exists('PurgeDockerNameRecord.txt') == False:
    newfile = open("PurgeDockerNameRecord.txt","w+")
    FirstTime = True
else:
    newfile = open("PurgeDockerNameRecord.txt","r+")
    cp_dict = ast.literal_eval(newfile.read()) # read file as dictionary format
    FirstTime = False

# log remove container
log_dict = {}
LogRemove = False

# compare container name
for i in range(len(lines)):
    createdTime = subprocess.check_output("docker inspect " + lines[i].strip('\n') + " --format='{{.Created}}'", shell=True)
    createdTime = createdTime[:10]
    createdObject = datetime.strptime(createdTime.strip('\n'), '%Y-%m-%d').date()
    record = date.today() - createdObject 
    if record > timedelta(days=90):
        containerName = subprocess.check_output("docker inspect " + lines[i].strip('\n') + " --format='{{.Name}}'", shell=True)
        if FirstTime == True:
            #print containerName.strip('/').strip('\n')
            cp_dict[containerName.strip('/').strip('\n')] = 1
            SendMail = True
        else:
            if containerName.strip('/').strip('\n') in cp_dict.keys():
                if int(cp_dict[containerName.strip('/').strip('\n')]) < 10:
                    cp_dict[containerName.strip('/').strip('\n')] = int(cp_dict[containerName.strip('/').strip('\n')]) + 1
                    SendMail = True
                else:
                    print('over 10 times')
                    #os.system('docker rm ' + lines[i].strip('\n'))
                    LogRemove = True
                    log_dict[containerName.strip('/').strip('\n')] = 'deleted'
            else:
                cp_dict.update({containerName.strip('/').strip('\n'): 1})
                SendMail = True

# Record the container which has been removed
if LogRemove:
    logfile = open("Over3MonthsDockerDeleteRecord.txt","w+a")
    logfile.write(str(log_dict))
    logfile.close()
if SendMail:
    msg = MIMEText("There is some container stopped over 3 months.\nWe will clean these stopped containers and release system resources after we inform this message 10 times.\nIf you still want to use these containers in the future, please backup them then.\nPlease check on " + socket.gethostname() +" (container_name: counting_times) as below:\n" + str(cp_dict))
    # the detail of mail
    msg['Subject'] = '[Important Information] There is some container stopped .'
    msg['From'] = "python_check@gmail.com"
    msg['To'] = "username@gmail.com"
    # Send the message via our own SMTP server, but don't include the envelope header.
    send = smtplib.SMTP('smtp.google.com')
    send.sendmail("python_check@gmail.com", ["username@gmail.com"], msg.as_string())
    send.quit()

print cp_dict
print ("----------------------------------------------------------")
newfile.seek(0)
newfile.write(str(cp_dict))
newfile.truncate()
newfile.close()
