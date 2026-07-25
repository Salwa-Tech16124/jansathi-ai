import json
import urllib.request
import urllib.error
import logging
from typing import Dict, Any, Optional
from app.config import settings

logger = logging.getLogger("jansathi.whatsapp")


class WhatsAppService:
    """
    Dedicated Client Service for WhatsApp Cloud API.
    Provides methods for sending text messages, marking incoming messages as read,
    parsing incoming Meta webhooks, and graceful error handling.
    """

    @property
    def access_token(self) -> Optional[str]:
        return settings.WHATSAPP_ACCESS_TOKEN

    @property
    def phone_number_id(self) -> Optional[str]:
        return settings.WHATSAPP_PHONE_NUMBER_ID

    @property
    def verify_token(self) -> str:
        return settings.WHATSAPP_VERIFY_TOKEN or "jansathi_verify_token_2026"

    def is_configured(self) -> bool:
        """Check if essential WhatsApp API credentials are set."""
        return bool(
            self.access_token and self.access_token.strip() and
            self.phone_number_id and self.phone_number_id.strip()
        )

    def send_text_message(self, to_number: str, text: str) -> bool:
        """
        Send a plain text WhatsApp message to a citizen phone number.
        
        API Endpoint: POST https://graph.facebook.com/v19.0/{phone_number_id}/messages
        """
        if not self.is_configured():
            logger.warning("[WhatsApp API] Missing credentials (WHATSAPP_ACCESS_TOKEN or WHATSAPP_PHONE_NUMBER_ID). Message not sent.")
            return False

        url = f"https://graph.facebook.com/v19.0/{self.phone_number_id.strip()}/messages"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token.strip()}"
        }

        # Format recipient number (ensure string digits)
        clean_recipient = "".join(filter(str.isdigit, str(to_number)))

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_recipient,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": text
            }
        }

        try:
            req_data = json.dumps(payload).encode('utf-8')
            request = urllib.request.Request(url, data=req_data, headers=headers, method="POST")

            with urllib.request.urlopen(request, timeout=10.0) as response:
                if response.status in (200, 201):
                    logger.info(f"[WhatsApp API] Successfully sent text message to {clean_recipient}.")
                    return True
                else:
                    logger.error(f"[WhatsApp API] Failed to send message. HTTP Status: {response.status}")
                    return False

        except urllib.error.HTTPError as http_err:
            body_err = http_err.read().decode('utf-8') if http_err.fp else ""
            logger.error(f"[WhatsApp API Error] HTTP {http_err.code}: {http_err.reason} - Details: {body_err}")
            return False
        except urllib.error.URLError as url_err:
            logger.error(f"[WhatsApp API Error] Network connection / Timeout error: {url_err.reason}")
            return False
        except Exception as err:
            logger.error(f"[WhatsApp API Error] Unexpected error during send: {err}")
            return False

    def mark_message_as_read(self, message_id: str) -> bool:
        """
        Mark an incoming WhatsApp message as read to display double blue checkmarks.
        """
        if not self.is_configured() or not message_id:
            return False

        url = f"https://graph.facebook.com/v19.0/{self.phone_number_id.strip()}/messages"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token.strip()}"
        }

        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }

        try:
            req_data = json.dumps(payload).encode('utf-8')
            request = urllib.request.Request(url, data=req_data, headers=headers, method="POST")
            with urllib.request.urlopen(request, timeout=5.0) as response:
                return response.status in (200, 201)
        except Exception as err:
            logger.warning(f"[WhatsApp API] Failed to mark message {message_id} as read: {err}")
            return False

    def extract_incoming_message(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse Meta WhatsApp Webhook JSON payload safely.
        
        Returns dict with keys: 'from_number', 'message_id', 'text', 'name' if valid text message,
        or None if payload is status update or unsupported type.
        """
        try:
            entries = payload.get("entry", [])
            if not entries:
                return None

            for entry in entries:
                changes = entry.get("changes", [])
                for change in changes:
                    value = change.get("value", {})
                    messages = value.get("messages", [])

                    if not messages:
                        # Event is likely a status update (sent/delivered/read)
                        continue

                    msg = messages[0]
                    msg_type = msg.get("type")

                    # We handle text messages
                    if msg_type == "text":
                        from_number = msg.get("from")
                        msg_id = msg.get("id")
                        text_body = msg.get("text", {}).get("body", "").strip()

                        # Extract contact profile name if present
                        contacts = value.get("contacts", [])
                        name = contacts[0].get("profile", {}).get("name", "Citizen") if contacts else "Citizen"

                        if from_number and text_body:
                            return {
                                "from_number": from_number,
                                "message_id": msg_id,
                                "text": text_body,
                                "name": name
                            }

                    else:
                        logger.info(f"[WhatsApp API] Received unsupported message type: {msg_type}. Skipping.")
                        return None

        except Exception as err:
            logger.error(f"[WhatsApp API] Error parsing incoming webhook JSON: {err}")
            return None

        return None


# Singleton WhatsApp service instance
whatsapp_service = WhatsAppService()
