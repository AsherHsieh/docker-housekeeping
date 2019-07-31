#!/usr/bin/python
import os
import mmap
import ast
import time

# list the name of all running container
myCmd = 'docker ps --format {{.Names}} > /tmp/docker_ps_Name.txt'
os.system(myCmd)

# save the running container to a file
NameData = open('/tmp/docker_ps_Name.txt', "r")
lines = NameData.readlines()
rc = mmap.mmap(NameData.fileno(), 0, access=mmap.ACCESS_READ)
NameData.close()

# open the container_registry
f = open('/home/developer/ServerMgt/container_registry')
s = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
f.close()

# open the config.py
py_dict ={}
python_var = open('/tmp/configs', "r")
py_dict = ast.literal_eval(python_var.read()) # read file as dictionary format
count_var = py_dict.get("CompareCounted")

# check CompareDockerNameRecord.txt is existed or not
cp_dict = {}
if os.path.exists('/tmp/CompareDockerNameRecord.txt') == False:
    newfile = open("/tmp/CompareDockerNameRecord.txt","w+")
    FirstTime = True
else:
    newfile = open("/tmp/CompareDockerNameRecord.txt","r+")
    cp_dict = ast.literal_eval(newfile.read()) # read file as dictionary format
    FirstTime = False

# log remove container 
log_dict = {}
LogRemove = False

# the container name has been registered in CompareDockerNameRecord.txt, but has been removed after owner received our mail.
if FirstTime == False:
    for keys in cp_dict.keys():
        if rc.find(keys) == -1:
            del cp_dict[keys]

# compare container name
for i in range(len(lines)):
    if s.find(lines[i].strip('\n')) == -1:                                                       # check if register
        if lines[i].startswith("project") == False:                                              # check if is project
            if FirstTime == True:                                                                # check if record file is first time created
                cp_dict[lines[i].strip('\n')] = 1
            else:                                                                                # the record file has existed
                if lines[i].strip('\n') in cp_dict.keys():                                       # the container name is already in file
                    if int(cp_dict[lines[i].strip('\n')]) < int(count_var):
                        cp_dict[lines[i].strip('\n')] = int(cp_dict[lines[i].strip('\n')]) + 1
                    else:
                        del cp_dict[lines[i].strip('\n')]                                        # remove the name from CompareDockerNameRecord.txt
                        os.system('docker stop ' + lines[i].strip('\n'))                         # stop the docker container
                        os.system('docker rm ' + lines[i].strip('\n'))
                        LogRemove = True
                        log_dict[lines[i].strip('\n')] = 'deleted'
                else:                                                                            # the container name first time show up in file
                    cp_dict.update({lines[i].strip('\n'): 1})
    else:
        if lines[i].strip('\n') in cp_dict.keys():
            del cp_dict[lines[i].strip('\n')]

# remove docker_ps_Name.txt
os.system('rm -f /tmp/docker_ps_Name.txt')

# Record the container which has been removed
if LogRemove:
    timestr = time.strftime("%Y-%m-%d")
    logfile = open("/tmp/DockerDeleteRecord-" + timestr + ".txt","w+a")
    logfile.write(str(log_dict))
    logfile.close()

#print cp_dict
newfile.seek(0)
newfile.write(str(cp_dict))
newfile.truncate()
newfile.close()
