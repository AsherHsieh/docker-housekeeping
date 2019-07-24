#!/usr/bin/python
import os
import subprocess
import ast
import time
from datetime import *

# list the name of all running container
myCmd = "docker ps -a | grep -i 'exited' | awk {'print $1'} > /tmp/docker_exited_id.txt"
os.system(myCmd)

# read the id
IDData = open('/tmp/docker_exited_id.txt', "r")
lines = IDData.readlines()
IDData.close()

# save the compare inforamtion
cp_dict = {}
if os.path.exists('/tmp/PurgeDockerNameRecord.txt') == False:
    newfile = open("/tmp/PurgeDockerNameRecord.txt","w+")
    FirstTime = True
else:
    newfile = open("/tmp/PurgeDockerNameRecord.txt","r+")
    cp_dict = ast.literal_eval(newfile.read()) # read file as dictionary format
    FirstTime = False

# log remove container
log_dict = {}
LogRemove = False

# compare container name
for i in range(len(lines)):
    createdTime = subprocess.check_output("docker inspect " + lines[i].strip('\n') + " --format='{{.Created}}'", shell=True)
    createdTime = createdTime[:10]                                                    # Get the docker-container created time
    createdObject = datetime.strptime(createdTime.strip('\n'), '%Y-%m-%d').date()     # Get today's date
    record = date.today() - createdObject
    if record > timedelta(days=90):                                                   # Compare if the created time is over 3 months
        containerName = subprocess.check_output("docker inspect " + lines[i].strip('\n') + " --format='{{.Name}}'", shell=True) # Get container name
        if FirstTime == True:
            cp_dict[containerName.strip('/').strip('\n')] = 1
        else:
            if containerName.strip('/').strip('\n') in cp_dict.keys():
                if int(cp_dict[containerName.strip('/').strip('\n')]) < 10:
                    cp_dict[containerName.strip('/').strip('\n')] = int(cp_dict[containerName.strip('/').strip('\n')]) + 1
                else:
                    #os.system('docker rm ' + lines[i].strip('\n'))
                    LogRemove = True
                    log_dict[containerName.strip('/').strip('\n')] = 'deleted'
            else:
                cp_dict.update({containerName.strip('/').strip('\n'): 1})

# remove docker_docker_exited_id.txt
os.system('rm -f /tmp/docker_exited_id.txt')

# Record the container which has been removedcd 
if LogRemove:
    timestr = time.strftime("%Y-%m-%d")
    logfile = open("/tmp/Over3MonthsDockerDeleteRecord-" + timestr + ".txt","w+a")
    logfile.write(str(log_dict))
    logfile.close()

#print cp_dict
newfile.seek(0)
newfile.write(str(cp_dict))
newfile.truncate()
newfile.close()
