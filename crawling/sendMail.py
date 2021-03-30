# ver 2.0 : 파일 처부 추가
# ver 2.1 : PC 정보 추가
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from os.path import basename
import os
import socket


from connection_info import get_connection_info

username = get_connection_info("gmail_user")
password = get_connection_info("gmail_pw")
smtp_host = get_connection_info("gmail_smtp_host")
pc_name = f"Host Name : {socket.gethostname()}"
user_name = f"USERNAME : {os.environ['USERNAME']}"
try:
    ip = socket.gethostbyname(socket.gethostname()).split('.')
    ip[1] = "xxx"
    ip[2] = "xxx"
    ip_addr = f"IP : {'.'.join(ip)}"
except:
    ip_addr = None

def sendMail(to=["sukchan.jung@sktelecom.com", "d99419a7.o365skt.onmicrosoft.com@apac.teams.ms"], title="title", text="Text", images=None, files=None):
    smtp = smtplib.SMTP(smtp_host, 587)
    # TLS 보안 시작
    smtp.starttls()
    # 로그인 인증
    smtp.login(username, password)

    msg_related = MIMEMultipart('related')
    text = f"[{pc_name}]\n[{user_name}]\n[{ip_addr}]\n{text}"
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
    try :
        path = "log/"
        lastfile = list(reversed([path+f for f in os.listdir(path) if not os.path.isdir(f)]))[0]
        files = []
        files.append(lastfile)
    except:
        files = None

    print(files)

    print("Host Name ", socket.gethostname())
    print("IP Address(Internal) : ", socket.gethostbyname(socket.gethostname()))
    print("IP Address(External) : ", socket.gethostbyname(socket.getfqdn()))

    sendMail(to=['neo2544@naver.com'], title="test", text="hello\nhello\n", files=files)
