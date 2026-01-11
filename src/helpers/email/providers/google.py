
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

            # Create HTML message
            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>OTP Verification</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        margin: 0;
                        padding: 20px;
                        background-color: #f4f4f4;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background-color: #ffffff;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 0 10px rgba(0,0,0,0.1);
                    }}
                    .header {{
                        text-align: center;
                        margin-bottom: 30px;
                    }}
                    .header h1 {{
                        color: #333;
                        margin: 0;
                        font-size: 24px;
                    }}
                    .otp-code {{
                        font-size: 32px;
                        font-weight: bold;
                        color: #007bff;
                        text-align: center;
                        margin: 30px 0;
                        padding: 20px;
                        background-color: #f8f9fa;
                        border-radius: 5px;
                        letter-spacing: 2px;
                    }}
                    .warning {{
                        background-color: #fff3cd;
                        border: 1px solid #ffeaa7;
                        padding: 15px;
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                    .warning strong {{
                        color: #856404;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        color: #666;
                        font-size: 14px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>SYANDE Meryl</h1>
                        <p>OTP Verification</p>
                    </div>
                    <p>Dear User,</p>
                    <p>We have received a request to verify your account. Please use the following One-Time Password (OTP) to complete the verification process:</p>
                    <div class="otp-code">{otp}</div>
                    <div class="warning">
                        <strong>Important Security Notice:</strong><br>
                        • This OTP is valid for 30 minutes only.<br>
                        • Do not share this code with anyone.<br>
                        • If you did not request this verification, please ignore this email.
                    </div>
                    <p>If you have any questions, please contact our support team.</p>
                    <p>Best regards,<br>The SYANDE Meryl Team</p>
                    <div class="footer">
                        <p>This is an automated message. Please do not reply to this email.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            message = MIMEText(html_content, 'html')
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
