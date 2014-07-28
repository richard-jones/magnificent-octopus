import smtplib, os
from portality.core import app

from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders

def send_mail(to, fro, subject, text, files=[], server="localhost"):
    assert type(to)==list
    assert type(files)==list

    msg = MIMEMultipart()
    msg['From'] = fro
    msg['To'] = COMMASPACE.join(to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach( MIMEText(text) )

    for file in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(file,"rb").read() )
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"'
                       % os.path.basename(file))
        msg.attach(part)

    # now deal with connecting to the server
    server = app.config.get("SMTP_SERVER")
    server_port = app.config.get("SMTP_PORT")
    smtp_user = app.config.get("SMTP_USER")
    smtp_pass = app.config.get("SMTP_PASS")

    smtp = smtplib.SMTP()  # just doing SMTP(server, server_port) does not work with Mailtrap
    # but doing .connect explicitly afterwards works both with Mailtrap and with Mandrill
    smtp.connect(server, server_port)

    if smtp_user is not None:
        smtp.login(smtp_user, smtp_pass)

    smtp.sendmail(fro, to, msg.as_string())
    smtp.close()