import logging
from typing import Dict, Any, Optional, List
from app.config import settings

logger = logging.getLogger("jansathi.twilio_whatsapp")

try:
    from twilio.rest import Client
    from twilio.request_validator import RequestValidator
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    logger.warning("[Twilio Service] Twilio SDK library not installed.")


class TwilioWhatsAppService:
    """
    Dedicated Service for Twilio WhatsApp Sandbox Integration.
    Encapsulates Twilio client initialization, signature validation, and outbound messaging.
    """

    def __init__(self):
        self._client: Optional[Any] = None
        self._validator: Optional[Any] = None

    @property
    def account_sid(self) -> Optional[str]:
        return settings.TWILIO_ACCOUNT_SID

    @property
    def auth_token(self) -> Optional[str]:
        return settings.TWILIO_AUTH_TOKEN

    @property
    def from_number(self) -> str:
        num = settings.TWILIO_WHATSAPP_NUMBER or "whatsapp:+14155238886"
        if not num.startswith("whatsapp:"):
            num = f"whatsapp:{num}"
        return num

    def is_configured(self) -> bool:
        """Check if Twilio credentials are provided and SDK is available."""
        return bool(
            TWILIO_AVAILABLE and
            self.account_sid and self.account_sid.strip() and
            self.auth_token and self.auth_token.strip()
        )

    def _get_client(self) -> Optional[Any]:
        """Lazy initialization of Twilio REST Client."""
        if not self.is_configured():
            return None

        if self._client is None:
            try:
                self._client = Client(self.account_sid.strip(), self.auth_token.strip())
            except Exception as err:
                logger.error(f"[Twilio Service] Failed to initialize Twilio Client: {err}")
                return None

        return self._client

    def format_whatsapp_number(self, phone: str) -> str:
        """Ensure phone number has 'whatsapp:' prefix and clean digits."""
        if phone.startswith("whatsapp:"):
            return phone
        clean_digits = "".join(filter(lambda c: c.isdigit() or c == '+', phone))
        if not clean_digits.startswith("+"):
            clean_digits = f"+{clean_digits}"
        return f"whatsapp:{clean_digits}"

    def validate_twilio_request(
        self,
        request_url: str,
        post_params: Dict[str, Any],
        signature_header: str
    ) -> bool:
        """
        Validate that an incoming HTTP request originated from Twilio using HMAC-SHA1 signature.
        Returns True if valid or if validator is disabled/unconfigured.
        """
        if not self.is_configured() or not signature_header:
            return True

        try:
            if self._validator is None:
                self._validator = RequestValidator(self.auth_token.strip())
            return self._validator.validate(request_url, post_params, signature_header)
        except Exception as err:
            logger.warning(f"[Twilio Service] Signature validation exception: {err}")
            return False

    def send_text_message(self, to_number: str, text: str) -> bool:
        """
        Send a text response to a WhatsApp user via Twilio API.
        """
        client = self._get_client()
        if not client:
            logger.warning(
                "[Twilio Service] Twilio credentials missing or invalid. Message not sent via Twilio."
            )
            return False

        recipient = self.format_whatsapp_number(to_number)

        try:
            message = client.messages.create(
                from_=self.from_number,
                to=recipient,
                body=text
            )
            logger.info(f"[Twilio Service] Message dispatched successfully to {recipient}. SID: {message.sid}")
            return True
        except Exception as err:
            logger.error(f"[Twilio Service Error] Failed to send WhatsApp message to {recipient}: {err}")
            return False

    def send_interactive_reply(
        self,
        to_number: str,
        text: str,
        options: Optional[List[str]] = None
    ) -> bool:
        """
        Send reply with formatted option callouts for interactive engagement.
        Fallback to text message with formatted bulleted choices.
        """
        formatted_body = text
        if options:
            formatted_body += "\n\n" + "\n".join([f"• {opt}" for opt in options])

        return self.send_text_message(to_number, formatted_body)


# Singleton instance
twilio_whatsapp_service = TwilioWhatsAppService()
