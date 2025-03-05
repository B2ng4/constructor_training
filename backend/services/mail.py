import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.core.config import configs
from backend.schemas.mail import mail_send
import asyncio


class EmailService:
    def __init__(self):
        self.username = configs.MAIL_USERNAME
        self.password = configs.MAIL_PASSWORD
        self.sender = configs.MAIL_FROM
        self.port = configs.MAIL_PORT
        self.server = configs.MAIL_SERVER
        self.use_tls = configs.MAIL_STARTTLS
        self.use_ssl = configs.MAIL_SSL_TLS

    def send_email(self, mail_send:mail_send):
        # Создаем сообщение
        message = MIMEMultipart()
        message["Subject"] = mail_send.subject
        message["From"] = self.sender
        message["To"] = mail_send.email
        body = mail_send.body
        message.attach(MIMEText(body, "plain"))

        try:
            if self.use_ssl:
                smtp = smtplib.SMTP_SSL(self.server, self.port)
            else:
                smtp = smtplib.SMTP(self.server, self.port)

                if self.use_tls:
                    smtp.starttls()
            smtp.login(self.username, self.password)
            smtp.send_message(message)
            smtp.quit()
            return True

        except Exception as e:
            print(e)



async def send_mail():
    mail = EmailService()
    pisimo = mail_send(email="timsidorin@gmail.com", subject="Добро пожаловать в EventsKnastu!", body="Вы успешно зарегистрировались в EventsKnastu!")
    print(mail.send_email(pisimo))

if __name__ == "__main__":
    asyncio.run(send_mail())

