#!/usr/bin/python
import os
import mmap
import subprocess
import ast
from datetime import *

# list the name of all running container
myCmd = "docker ps -a | grep -i 'exited' | awk {'print $1'} > /tmp/docker_exited_id.txt"
os.system(myCmd)

# read the id
IDData = open('/tmp/docker_exited_id.txt', "r")
lines = IDData.readlines()
rc = mmap.mmap(IDData.fileno(), 0, access=mmap.ACCESS_READ)
IDData.close()

# open the config.py
py_dict ={}
python_var = open('/tmp/configs', "r")
py_dict = ast.literal_eval(python_var.read()) # read file as dictionary format
count_var = py_dict.get("ExitedCounted")
days_var = py_dict.get("OverdaysCounted")

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

# the container name has been registered in PurgeDockerNameRecord.txt, but has been removed after owner received our mail.
if FirstTime == False:
    for keys in cp_dict.keys():
        findId = subprocess.check_output("docker ps | grep " + keys + " | awk {'print $1'}", shell=True)
        if rc.find(findId) == -1:
            del cp_dict[keys]

# compare container name
for i in range(len(lines)):
    createdTime = subprocess.check_output("docker inspect " + lines[i].strip('\n') + " --format='{{.State.FinishedAt}}'", shell=True)
    createdTime = createdTime[:10]                                                               # Get the docker-container created time
    createdObject = datetime.strptime(createdTime.strip('\n'), '%Y-%m-%d').date()                # Get today's date
    record = date.today() - createdObject
    containerName = subprocess.check_output("docker inspect " + lines[i].strip('\n') + " --format='{{.Name}}'", shell=True) # Get container name
    if record > timedelta(days=int(days_var)):                                                   # Compare if the created time is over 3 months
        if FirstTime == True:
            cp_dict[containerName.strip('/').strip('\n')] = 1
        else:
            if containerName.strip('/').strip('\n') in cp_dict.keys():
                if int(cp_dict[containerName.strip('/').strip('\n')]) < int(count_var):
                    cp_dict[containerName.strip('/').strip('\n')] = int(cp_dict[containerName.strip('/').strip('\n')]) + 1
                else:
                    del cp_dict[containerName.strip('/').strip('\n')]
                    os.system('docker rm ' + lines[i].strip('\n'))
                    LogRemove = True
                    log_dict[containerName.strip('/').strip('\n')] = 'deleted'
            else:
                cp_dict.update({containerName.strip('/').strip('\n'): 1})
    else:
        if containerName.strip('/').strip('\n') in cp_dict.keys():
            del cp_dict[containerName.strip('/').strip('\n')]


# remove docker_docker_exited_id.txt
os.system('rm -f /tmp/docker_exited_id.txt')

# Record the container which has been removedcd 
if LogRemove:
    timestr = date.today()
    logfile = open("/tmp/Over3MonthsDockerDeleteRecord-" + str(timestr) + ".txt","w+a")
    logfile.write(str(log_dict))
    logfile.close()

#print cp_dict
newfile.seek(0)
newfile.write(str(cp_dict))
newfile.truncate()
newfile.close()
