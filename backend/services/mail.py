from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from backend.core.config import configs



class EmailService:
    def __init__(self):
        self.conf = ConnectionConfig(
            MAIL_USERNAME=configs.MAIL_USERNAME,
            MAIL_PASSWORD=configs.MAIL_PASSWORD,
            MAIL_FROM=configs.MAIL_FROM,
            MAIL_PORT=configs.MAIL_PORT,
            MAIL_SERVER=configs.MAIL_SERVER,
            MAIL_TLS=configs.MAIL_TLS,
            MAIL_SSL=configs.MAIL_SSL,
        )

    async def send_welcome_email(self, email: str):
        message = MessageSchema(
            subject="Добро пожаловать в EventsKnagu",
            recipients=[email],
            body="Спасибо за регистрацию!",
        )
        fm = FastMail(self.conf)
        await fm.send_message(message)

