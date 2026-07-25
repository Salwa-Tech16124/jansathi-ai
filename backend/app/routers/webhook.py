import logging
from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.twilio_whatsapp_service import twilio_whatsapp_service
from app.services.ai_service import ai_case_worker

logger = logging.getLogger("jansathi.twilio_webhook")

router = APIRouter(tags=["Twilio WhatsApp Webhook"])


@router.post("/webhook")
async def handle_twilio_webhook(
    request: Request,
    From: str = Form(None),
    Body: str = Form(None),
    MessageSid: str = Form(None),
    db: Session = Depends(get_db)
):
    """
    POST /webhook endpoint receiving incoming WhatsApp messages from Twilio Sandbox.
    
    Twilio posts standard HTTP form data:
    - From: e.g. 'whatsapp:+919876543210'
    - Body: Citizen message text
    - MessageSid: Twilio message identifier
    """
    # If parameters were not injected by Form parser, parse request form data manually
    if not From or not Body:
        try:
            form_data = await request.form()
            From = From or form_data.get("From")
            Body = Body or form_data.get("Body")
            MessageSid = MessageSid or form_data.get("MessageSid")
        except Exception:
            pass

    sender_phone = From or ""
    message_text = (Body or "").strip()

    if not sender_phone or not message_text:
        logger.warning("[Twilio Webhook] Received empty or invalid payload.")
        # Return valid TwiML response to satisfy Twilio
        twiml_content = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response></Response>"
        return Response(content=twiml_content, media_type="application/xml", status_code=200)

    logger.info(f"[Twilio Inbound] Message from {sender_phone} (Sid: {MessageSid}): '{message_text}'")

    # Optional Twilio request validation
    signature_header = request.headers.get("X-Twilio-Signature", "")
    request_url = str(request.url)
    if signature_header and twilio_whatsapp_service.is_configured():
        # Validate signature if configured
        post_data = dict(await request.form()) if hasattr(request, "form") else {}
        is_valid = twilio_whatsapp_service.validate_twilio_request(request_url, post_data, signature_header)
        if not is_valid:
            logger.warning(f"[Twilio Webhook] Invalid signature header for URL: {request_url}")

    # Process incoming message using existing AI Case Worker
    try:
        ai_res = ai_case_worker.analyze_and_respond(message_text, db)
        reply_text = ai_res.get("reply", "")

        # Format matched schemes cleanly for WhatsApp output
        matched_schemes = ai_res.get("matched_schemes", [])
        if matched_schemes:
            reply_text += "\n\n📌 *Matched Government Schemes:*"
            for idx, scheme in enumerate(matched_schemes[:3], 1):
                reply_text += (
                    f"\n\n*{idx}. {scheme['title']}*\n"
                    f"• *Category:* {scheme['category']}\n"
                    f"• *Eligibility:* {scheme['eligibility']}\n"
                    f"• *Documents Needed:* {scheme['required_documents']}"
                )

        # Dispatch reply via Twilio WhatsApp API
        twilio_whatsapp_service.send_text_message(sender_phone, reply_text)

    except Exception as err:
        logger.error(f"[Twilio Webhook Error] Error processing message: {err}")
        twilio_whatsapp_service.send_text_message(
            sender_phone,
            "Namaste! JanSathi AI system is currently processing your request. Please try again shortly."
        )

    # Return empty TwiML XML response to acknowledge receipt to Twilio
    twiml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response></Response>"
    return Response(content=twiml, media_type="application/xml", status_code=200)


@router.get("/webhook")
def twilio_webhook_status():
    """
    GET /webhook helper endpoint for health check.
    """
    return {
        "status": "ok",
        "service": "Twilio WhatsApp Sandbox Webhook",
        "configured": twilio_whatsapp_service.is_configured()
    }
