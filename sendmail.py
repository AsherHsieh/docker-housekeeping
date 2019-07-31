#!/usr/bin/python
import smtplib
import ast

# Import the email modules we'll need
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# mail information
sender = "docker_housekeeper@gmail.com"
receiver = ['username@gmail.com']
SendFlag = False

# Counting Down Days
py_dict ={}
python_var = open('/ailab/configs', "r")
py_dict = ast.literal_eval(python_var.read()) # read file as dictionary format
totalday = py_dict.get("CompareCounted")

msg = MIMEMultipart('alternative')

# fixed template
html = '<html><head></head><body><p>To whom it may concern: <br><br>Our automatic system housekeeper detected below <b>Unregistered</b> Containers. <br>when <b>Days Count Down</b> reaches <font color="red">0</font>. Please refer to <b><font color="purple">Remedy Instructions</font></b> at the bottom to save your containers:<br><br></p>'

table = '<table border="1"><tr><td><b>Name</b></td><td><b>Days Count Down</b></td></tr>'
remedy = '<b><font color="purple">Remedy Instructions:</font></b><br><p>1. Login to corresponding server<br>2. Edit /home/developer/ServerMgt/container_registry<br>3. Refer to procedures in this <a href="http://">SOP</a> (point 6) to register your container, typically as below example (<b>Bold</b> entries are mandatory):<br></p></br><table border="1"><tr><td><font color="blue"><b>#Ports:</b> 10000<br><b>Owner:</b> Asher<br><b>Container:</b> asher_ansible_test<br><b>Description:</b> To test ansible utility<br>Binds: /home/developer/Users/asher/scripts:/ansible/scripts<br>Date: 2019-07-25<br></font></td></tr></table></body></html>'
# fixed template End

# save the running container to a file
NameData = open('/ailab/inventory_date/hosts', "r")
lines = NameData.readlines()
NameData.close()

# write alert mail
strTable = ""
mail_dict = {}
for i in range(len(lines)):
    hostName = lines[i].strip('\n').strip('\r')
    newfile = open("/ailab/log/" + hostName + "/tmp/CompareDockerNameRecord.txt", "r+")
    mail_dict = ast.literal_eval(newfile.read())
    if bool(mail_dict):
        SendFlag = True
        strTable += '<b><font color="red">' + hostName + '</font></b><br><br>'
        strTable += table
        for key, value in mail_dict.iteritems():
            countdown = int(totalday) - int(value)
            if countdown == 0:
                valueTable = '<td><font color="red" style="background-color:#FFFF00">' + str(countdown) + '</font></td></tr>'
                keyTable = '<tr><td><font color="red" style="background-color:#FFFF00">' + key + '</font></td>'
            else:
                valueTable = '<td>' + str(countdown) + '</td></tr>'
                keyTable = '<tr><td>' + key + '</td>'
            strTable += keyTable + valueTable
        strTable += '</table><br>'

newfile.close()
#print strTable # check alert mail table

if SendFlag == True:
    # mail content
    content = MIMEText(html + strTable + remedy, 'html', _charset='utf-8')
    # the detail of mail
    msg['Subject'] = 'Warning: Unregistered Docker Containers Detected!!'
    msg['From'] = sender
    msg['To'] = ",".join(receiver)
    msg.attach(content)
    # Send the message via our own SMTP server, but don't include the envelope header.
    send = smtplib.SMTP('smtp.gmail.com')
    send.sendmail(sender, receiver, msg.as_string())
    send.quit()
