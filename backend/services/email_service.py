import logging
from typing import List
from ..utils.gmail_auth import get_gmail_service
from ..utils.email_parser import parse_email
from ..models.schemas import EmailBase

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.service = None

    def _get_service(self):
        if not self.service:
            self.service = get_gmail_service()
        return self.service

    def fetch_sent_emails(self, max_results: int = 3) -> List[EmailBase]:

        try:
            service = self._get_service()
            results = service.users().messages().list(
                userId="me", labelIds=["SENT"], maxResults=3
            ).execute()

            messages = results.get("messages", [])
            parsed_emails = []

            for msg in messages:
                try:
                    msg_detail = service.users().messages().get(
                        userId="me", id=msg["id"]
                    ).execute()
                    parsed = parse_email(msg_detail)
                    parsed_emails.append(EmailBase(**parsed))
                except Exception as e:
                    logger.error(f"Error parsing email {msg['id']}: {str(e)}")
                    continue

            return parsed_emails

        except Exception as e:
            logger.error(f"Error fetching emails: {str(e)}")
            raise Exception(f"Failed to fetch emails: {str(e)}")


email_service = EmailService()
