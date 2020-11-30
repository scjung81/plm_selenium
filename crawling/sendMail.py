# ver 2.0 : 파일 처부 추가
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from os.path import basename
import os

from crawling.connection_info import get_connection_info

username = get_connection_info("gmail_user")
password = get_connection_info("gmail_pw")
smtp_host = get_connection_info("gmail_smtp_host")

def sendMail(to=["jungil.kwon@sktelecom.com", "d99419a7.o365skt.onmicrosoft.com@apac.teams.ms"], title="title", text="Text", images=None, files=None):
    smtp = smtplib.SMTP(smtp_host, 587)
    # TLS 보안 시작
    smtp.starttls()
    # 로그인 인증
    smtp.login(username, password)

    msg_related = MIMEMultipart('related')

    plain_part = MIMEText(text)
    msg_related.attach(plain_part)

    msg_related['Subject'] = title
    msg_related['To'] = ', '.join(to)

    msg_alternative = MIMEMultipart('alternative')
    msg_related.attach(msg_alternative)


    if images:
        for image in images:
            with open(image['path'], 'rb') as f:
                msg_image = MIMEImage(f.read())
                msg_image.add_header('Content-ID', '<{0}>'.format(image['id']))
                msg_related.attach(msg_image)


    if files:
        for f in files or []:
            with open(f, "rb") as fil:
                part = MIMEApplication(fil.read(), Name=basename(f))
            # After the file is closed
            part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
            msg_related.attach(part)

    # Sending the mail
    smtp.sendmail('sdqiskt@gmail.com', to, msg_related.as_string())

    smtp.quit()
    print("success mail sending")

## Start
if __name__ == "__main__":
    lastdir = list(reversed(["data/" + f for f in os.listdir("data") if not "." in f]))[0]
    last_dt = lastdir.split("/")[1]
    print(lastdir, last_dt)

    print(print(os.getcwd()))
    files = []
    files.append(f"{lastdir}/plm_swver_DataWarehouse_{last_dt}.xls")
    print(files)

    sendMail(files=files)

