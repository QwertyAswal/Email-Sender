from flask import Flask, request
import os
import json
import csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


app = Flask(__name__)
s = smtplib.SMTP('smtp.gmail.com', 587)
s.starttls()
yourMail = "YOUR EMAIL"
yourPwd = "YOUR PWD"
s.login(yourMail, yourPwd)

path = 'data/'

@app.route('/data', methods=['POST'])
def post_method():
    data = json.loads(request.data)
    print(data)
    dirs = os.listdir(path)
    device_dir = os.path.join(path, data["email"])
    if data["email"] not in dirs:
        os.mkdir(device_dir)
    reports = os.listdir(device_dir)
    if (data["report"]+".csv") not in reports:
        with open(os.path.join(device_dir, data["report"]+".csv"), 'w') as f:
            f.write("Employee,Contact Employee,Inout,Timestamp\n")
    with open(os.path.join(device_dir, data["report"]+".csv"), 'a') as f:
        f.write((str(data["employee"])+','+str(data["contactEmployee"])+','+str(data["inout"])+','+str(data["timestamp"])+"\n"))
    return 'success data'



@app.route('/send', methods=['POST'])
def send_email():
    data = json.loads(request.data)
    dirs = os.listdir(path)
    msg = MIMEMultipart()
    fromaddr = yourMail
    msg['From'] = fromaddr
    msg['Subject'] = "Timely Report of Devices"
    if data["email"] not in dirs:
        body = "No new entries."
        msg.attach(MIMEText(body, 'plain'))
        text = msg.as_string()
        s.sendmail(fromaddr, data["email"], text)
    else:
        body = "CSV files are attached"
        msg.attach(MIMEText(body, 'plain'))
        device_dir = os.path.join(path, data["email"])
        devices = os.listdir(device_dir)
        for i in devices:
            attachment = open(os.path.join(device_dir, i), "rb")
            p = MIMEBase('application', 'octet-stream')
            p.set_payload((attachment).read())
            encoders.encode_base64(p)
            p.add_header('Content-Disposition', "attachment; filename= %s" % i)
            msg.attach(p)
            attachment.close()
            os.remove(os.path.join(device_dir, i))
        os.rmdir(device_dir)
        text = msg.as_string()
        s.sendmail(fromaddr, data["email"], text)
    return 'send successful'

if __name__ == '__main__':
    app.run()
