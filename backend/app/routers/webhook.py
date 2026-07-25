import logging
from xml.sax.saxutils import escape
from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.services.twilio_whatsapp_service import twilio_whatsapp_service
from app.services.ai_service import ai_case_worker
from app.services.sarvam_service import sarvam_client

logger = logging.getLogger("jansathi.twilio_webhook")

router = APIRouter(tags=["Twilio WhatsApp Webhook"])


@router.post("/webhook")
@router.post("/webhook/incoming")
async def handle_twilio_webhook(
    request: Request,
    From: str = Form(None),
    Body: str = Form(None),
    MessageSid: str = Form(None),
    NumMedia: str = Form(None),
    MediaUrl0: str = Form(None),
    MediaContentType0: str = Form(None),
    db: Session = Depends(get_db)
):
    """
    POST /webhook endpoint receiving incoming WhatsApp text & voice messages from Twilio Sandbox.
    Supports both text messages and voice notes via Sarvam AI Speech-to-Text.
    """
    media_url = MediaUrl0
    media_type = MediaContentType0

    # Parse request form data if not automatically injected
    try:
        form_data = await request.form()
        From = From or form_data.get("From")
        Body = Body or form_data.get("Body")
        MessageSid = MessageSid or form_data.get("MessageSid")
        media_url = media_url or form_data.get("MediaUrl0")
        media_type = media_type or form_data.get("MediaContentType0")
        NumMedia = NumMedia or form_data.get("NumMedia")
    except Exception:
        pass

    sender_phone = From or ""
    message_text = (Body or "").strip()

    # Voice Note Handling: Only trigger STT if an audio file was actually attached
    has_audio = bool(
        (media_type and "audio" in media_type.lower()) or
        (media_url and media_url.strip() and str(media_url) != "None")
    )

    if has_audio and media_url:
        logger.info(f"[Twilio Inbound Voice] Voice note received from {sender_phone}: {media_url}")
        transcribed = sarvam_client.transcribe_audio_url(media_url)
        if transcribed:
            logger.info(f"[Twilio Inbound Voice] Transcribed text: '{transcribed}'")
            message_text = transcribed
        else:
            if not message_text:
                message_text = "voice note inquiry for government scheme"

    if not sender_phone or not message_text:
        logger.warning("[Twilio Webhook] Received empty or invalid payload.")
        twiml_content = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response></Response>"
        return Response(content=twiml_content, media_type="application/xml; charset=utf-8", status_code=200)

    logger.info(f"[Twilio Inbound] Message from {sender_phone} (Sid: {MessageSid}): '{message_text}'")

    try:
        # Process incoming message using AI Case Worker
        ai_res = ai_case_worker.analyze_and_respond(message_text, db, session_id=sender_phone)
        reply_text = ai_res.get("reply", "")

        # Append Public Website Link so citizens can open the React Web UI on ngrok
        web_url = getattr(settings, "PUBLIC_WEBSITE_URL", "https://ceroplastic-evaluative-emeline.ngrok-free.dev")
        website_callout = f"\n\n🌐 For full interactive portal, reminders & web chat, visit:\n{web_url}"
        if web_url not in reply_text:
            reply_text += website_callout

        # Also attempt dispatch via REST API if configured (catch REST API 429 quota limits gracefully)
        if twilio_whatsapp_service.is_configured():
            try:
                twilio_whatsapp_service.send_text_message(sender_phone, reply_text)
            except Exception as rest_err:
                logger.warning(f"[Twilio REST API Notice] REST API dispatch limit notice: {rest_err}")

        # Return direct TwiML XML with <Message> body for instant WhatsApp delivery (unaffected by REST API daily limit)
        escaped_reply = escape(reply_text)
        twiml_content = f"<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response><Message>{escaped_reply}</Message></Response>"
        return Response(content=twiml_content.encode("utf-8"), media_type="text/xml", status_code=200)

    except Exception as err:
        logger.error(f"[Twilio Webhook Error] Error processing message: {err}", exc_info=True)
        err_msg = "Namaste! JanSathi AI system is currently processing your request. Please try again shortly."
        escaped_err = escape(err_msg)
        twiml_content = f"<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response><Message>{escaped_err}</Message></Response>"
        return Response(content=twiml_content.encode("utf-8"), media_type="text/xml", status_code=200)


@router.get("/webhook")
@router.get("/webhook/incoming")
def twilio_webhook_status():
    """
    GET /webhook helper endpoint for health check.
    """
    return {
        "status": "ok",
        "service": "Twilio WhatsApp Sandbox Webhook",
        "configured": twilio_whatsapp_service.is_configured()
    }
