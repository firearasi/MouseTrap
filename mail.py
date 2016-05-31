SMTPserver='smtp.qq.com'
sender="firearasi@qq.com"
destination=["chengyanslnc@gmail.com"]

USERNAME="firearasi"
PASSWORD="a1siteru"




subject="Sent from Python"

def sendtextmail(destination,subject,content):

  import sys,os,re
  from smtplib import SMTP_SSL as SMTP
  from email.mime.text import MIMEText

  try:
   msg=MIMEText(content,'plain')
   msg['Subject']=subject
   msg['From']=sender
  
   conn=SMTP(SMTPserver)
   conn.set_debuglevel(False)
   conn.login(USERNAME,PASSWORD)
   try:
      conn.sendmail(sender,destination,msg.as_string())
   finally:
      conn.quit()
  except Exception as e:
   sys.exit("mail failed;%s"%str(e))
