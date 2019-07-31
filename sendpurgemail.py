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
totalday = py_dict.get("ExitedCounted")


msg = MIMEMultipart('alternative')

# fixed template
html = '<html><head></head><body><p>To whom it may concern: <br><br>Our automatic system housekeeper detected below Containers have been <b>Exited</b> for over <b>3 months</b>.<br>They will be <b>Deleted</b> when <b>Days Count Down</b> reaches <b><font color="red">0</font></b>. Please refer to <b><font color="purple">Remedy Instructions</font></b> at the bottom to save your containers:<br></p>'

table = '<table border="1"><tr><td><b>Name</b></td><td><b>Days Count Down</b></td></tr>'
remedy = '<b><font color="purple">Remedy Instructions</font></b><br><p>1. Login to corresponding server<br>2. docker start the inactive container in order to refresh the container date<br>3. docker stop the same container if not using at the moment<br></p></body></html>'
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
    newfile = open("/ailab/log/" + hostName + "/tmp/PurgeDockerNameRecord.txt", "r+")
    mail_dict = ast.literal_eval(newfile.read())
    if bool(mail_dict):
        SendFlag = True
        strTable += '<b><font color="red">' + hostName + '</font></b><br><br>'
        strTable += table
        for key, value in mail_dict.iteritems():
            countdown = int(totalday) - int(value)
            if countdown == 0:
                keyTable = '<tr><td><font color="red" style="background-color:#FFFF00">' + key + '</font></td>'
                valueTable = '<td><font color="red" style="background-color:#FFFF00">' + str(countdown) + '</font></td></tr>'
            else:
                keyTable = '<tr><td>' + key + '</td>'
                valueTable = '<td>' + str(countdown) + '</td></tr>'
            strTable += keyTable + valueTable
        strTable += '</table><br>'

newfile.close()
#print strTable # check alert mail table

if SendFlag == True:
    # mail content
    content = MIMEText(html + strTable + remedy, 'html', _charset='utf-8')
    # the detail of mail
    msg['Subject'] = 'Warning: Exited Docker Containers Detected!!'
    msg['From'] = sender
    msg['To'] = ",".join(receiver)
    msg.attach(content)
    # Send the message via our own SMTP server, but don't include the envelope header.
    send = smtplib.SMTP('smtp.gmail.com')
    send.sendmail(sender, receiver, msg.as_string())
    send.quit()
