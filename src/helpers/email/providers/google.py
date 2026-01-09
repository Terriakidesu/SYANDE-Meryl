
from ....models.provider import MailProvider


class GoogleProvider(MailProvider):

    def __init__(self):
        super().__init__()

    def send_mail(self, email: str, otp: str):
        # TODO: Implement gmail api for otp
        raise NotImplementedError()
