SMTPserver='smtp.qq.com'
sender="firearasi@qq.com"


USERNAME="firearasi"
PASSWORD="a1siteru"



subject="Sent from Python"

def sendmail(destination,subject,content,img=None):

  import sys,os,re
  from smtplib import SMTP_SSL as SMTP
  from email.mime.text import MIMEText
  from email.mime.multipart import MIMEMultipart
  from email.mime.image import MIMEImage
  import mimetypes
  try:
   msg=MIMEMultipart()
   
   msg['Subject']=subject
   msg['From']=sender
   msg['To']=destination
   
   body=MIMEText(content)
   msg.attach(body)
   
   if img is not None:
    try:
      file=open(img,'rb')
      att=MIMEImage(file.read())
      att.add_header('Content-Disposition','attachment',filename=img)
      msg.attach(att)
    except Exception as e:
      print("Error: ",e)
    finally:
      file.close()
   server=SMTP(SMTPserver)
   server.set_debuglevel(False)
   server.login(USERNAME,PASSWORD)
   try:
      server.sendmail(sender,destination,msg.as_string())
   finally:
      server.quit()
  except Exception as e:
   sys.exit("mail failed;%s"%str(e))
