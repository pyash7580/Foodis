
import ssl
import logging
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.backends.smtp import EmailBackend

logger = logging.getLogger(__name__)


class ConsoleEmailBackend(BaseEmailBackend):
    """
    Development backend: prints emails to console instead of sending.
    Use when EMAIL_HOST_PASSWORD is not set so OTP still works locally.
    """
    def send_messages(self, email_messages):
        for message in email_messages:
            subject = message.subject
            body = message.body
            to = list(message.to) if message.to else []
            if hasattr(message, 'alternatives') and message.alternatives:
                body = message.alternatives[0][0] if message.alternatives else body
            logger.info(
                "[CONSOLE EMAIL] To: %s | Subject: %s\n%s",
                to, subject, body[:500] if body else "(no body)"
            )
            print(f"\n{'='*60}\n[CONSOLE EMAIL] To: {to}\nSubject: {subject}\n{body[:400]}...\n{'='*60}\n")
        return len(email_messages)


class UnsafeEmailBackend(EmailBackend):
    """
    SMTP email backend that ignores SSL certificate verification.
    ONLY for use in development/local environments where CA bundles may be missing.
    """
    def open(self):
        if self.connection:
            return False
        try:
            # Create an unverified SSL context
            context = ssl._create_unverified_context()
            
            # Open connection with timeout
            self.connection = self.connection_class(
                self.host, self.port, timeout=self.timeout
            )
            self.connection.ehlo()
            
            if self.use_tls:
                self.connection.starttls(context=context)
                self.connection.ehlo()
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except Exception as e:
            if not self.fail_silently:
                raise
            logger.error(f"Failed to open email connection: {e}")
            return False
