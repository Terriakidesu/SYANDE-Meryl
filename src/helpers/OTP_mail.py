import resend

from ..Settings import Settings


def send_otp_email(email, otp):
    resend.api_key = Settings.secrets.resend_api_key

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
