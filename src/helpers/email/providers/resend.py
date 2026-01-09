import resend

from ....models.provider import MailProvider
from ....Settings import Settings


class ResendProvider(MailProvider):

    def __init__(self):
        super().__init__()

        resend.api_key = Settings.secrets.resend_api_key

    def send_mail(self, email: str, otp: str):

        resend.Emails.send({
            "from": "Meryl <meryl@syande-mail.hopto.org>",
            "to": email,
            "subject": "Your OTP",
            "template": {
                    "id": "otp-mail",
                    "variables": {
                        "OTP": f"{otp}"
                    }
            }
        })
