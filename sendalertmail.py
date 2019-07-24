#!/usr/bin/python
import smtplib
import ast

# Import the email modules we'll need
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# mail information
sender = "python_check@gmail.com"
receiver = "username@gmail.com"

# Counting Down Days
totalday = 5

msg = MIMEMultipart('alternative')

# fixed template
html = """\
<html>
  <head></head>
  <body>
    <p>
       To whom it may concern: <br>
       <br>
       Our automatic system housekeeper detected below <b>Unregistered</b> Containers. <br>
       They will be <b>Deleted</b> unless you correctly register them per instructions at page bottom: <br>
    </p>
  </body>
</html>
"""
table = '<table border="1"><tr><td><b>Name</b></td><td><b>Days Count Down</b></td></tr>'
remedy = '<b><font color="red">Remedy Instructions:</font></b><br>'
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
    newfile = open("/ailab/inventory_date/backup/" + hostName + "/tmp/CompareDockerNameRecord.txt", "r+")
    mail_dict = ast.literal_eval(newfile.read())
    if bool(mail_dict):
        strTable += '<b><font color="red">' + hostName + '</font></b><br>'
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

# mail content
content = MIMEText(html + strTable + remedy, 'html')

# the detail of mail
msg['Subject'] = 'Warning: Unregistered Docker Containers Detected!!'
msg['From'] = sender
msg['To'] = receiver
msg.attach(content)

# Send the message via our own SMTP server, but don't include the envelope header.
send = smtplib.SMTP('smtp.google.com')
send.sendmail(sender, receiver, msg.as_string())
send.quit()
