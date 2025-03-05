import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.core.config import configs


class EmailService:
    def __init__(self):
        self.username = configs.MAIL_USERNAME
        self.password = configs.MAIL_PASSWORD
        self.sender = configs.MAIL_FROM
        self.port = configs.MAIL_PORT
        self.server = configs.MAIL_SERVER
        self.use_tls = configs.MAIL_STARTTLS
        self.use_ssl = configs.MAIL_SSL_TLS

    def send_welcome_email(self, email: str):
        # Создаем сообщение
        message = MIMEMultipart()
        message["Subject"] = "Добро пожаловать в EventsKnagu"
        message["From"] = self.sender
        message["To"] = email
        body = "Спасибо за регистрацию!"
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

        except:
            return False

