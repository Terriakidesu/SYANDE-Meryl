from .providers import Resend, Google


def send_otp_email(email, otp, provider=Resend):

    provider.send_mail(email, otp)
