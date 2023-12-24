import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import MAIL_USERNAME, MAIL_PASSWORD, MAIL_SERVER


def mail_sender(data):
    msg = MIMEMultipart()

    msg['From'] = MAIL_USERNAME
    msg['To'] = data["recipient"]
    msg['Subject'] = data["title"]

    msg.attach(MIMEText(data["body"], 'plain'))
    text = msg.as_string()

    with smtplib.SMTP_SSL(MAIL_SERVER, 465) as server:
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.sendmail(MAIL_USERNAME, data["recipient"], text)
        server.quit()

    return None
