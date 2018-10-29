#coding=utf-8
import sys
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP
import smtplib
import sys

def DebugSendMail(title,log):
    sender = 'pakingLogParser'
    passwd = 'paKing0606'
    #receivers = ['steven.chang@pakingtek.com']
    receivers = ['steven.chang@pakingtek.com','sarina.chao@pakingtek.com','samuel.chen@pakingtek.com','eric.teng@pakingtek.com','allen.hsiao@pakingtek.com']
    cc = ['allen.hsiao@pakingtek.com']
    emails = [elem.strip().split(',') for elem in receivers]
    msg = MIMEMultipart()
    msg['Subject'] = "Detect Failed"
    msg['From'] = "Log parser system"
    msg['To'] = ','.join(receivers)
    #msg['Cc'] = ','.join(cc)
    msg.preamble = 'Multipart massage.\n'
    part = MIMEText(title+"\n---------------------\n"+log)
    msg.attach(part)

    smtp = smtplib.SMTP("smtp.gmail.com:587")
    smtp.ehlo()
    smtp.starttls()
    smtp.login(sender, passwd)

    smtp.sendmail(msg['From'], emails , msg.as_string())
    print ('Send mails to',msg['To'])

