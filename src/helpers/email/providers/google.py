
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

from ....models.provider import MailProvider
from ....Settings import Settings


class GoogleProvider(MailProvider):

    def __init__(self):
        super().__init__()
        self.creds = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Gmail API using OAuth2 credentials."""
        try:
            # Create credentials from refresh token
            self.creds = Credentials(
                None,
                refresh_token=Settings.secrets.gmail_refresh_token,
                token_uri='https://oauth2.googleapis.com/token',
                client_id=Settings.secrets.gmail_client_id,
                client_secret=Settings.secrets.gmail_client_secret
            )

            # Refresh the token if needed
            if self.creds.expired:
                self.creds.refresh(Request())

        except Exception as e:
            raise Exception(f"Failed to authenticate with Gmail API: {str(e)}")

    def send_mail(self, email: str, otp: str):
        """Send OTP email using Gmail API."""
        try:
            # Create Gmail API service
            service = build('gmail', 'v1', credentials=self.creds)

            # Create message
            message = MIMEText(f'Your OTP code is: {otp}')
            message['to'] = email
            message['subject'] = 'Your OTP Code'

            # Option 1: Use authenticated user's email ('me')
            # message['from'] = 'me'

            # Option 2: Use a custom from name (but still sends from authenticated account)
            message['from'] = 'SYANDE Meryl <me>'

            # Option 3: Use a verified alias if you have one
            # message['from'] = 'your-verified-alias@gmail.com'

            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            # Create message body
            message_body = {'raw': raw_message}

            # Send message
            service.users().messages().send(userId='me', body=message_body).execute()

        except Exception as e:
            raise Exception(f"Failed to send email via Gmail API: {str(e)}")
