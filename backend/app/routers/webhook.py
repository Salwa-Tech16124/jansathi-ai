import logging
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.services.whatsapp_service import whatsapp_service
from app.services.ai_service import ai_case_worker

logger = logging.getLogger("jansathi.webhook")

router = APIRouter(tags=["WhatsApp Webhook"])


@router.get("/webhook")
def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    """
    GET /webhook endpoint required by Meta WhatsApp Cloud API for webhook verification.
    """
    expected_token = settings.WHATSAPP_VERIFY_TOKEN or "jansathi_verify_token_2026"

    if hub_mode == "subscribe" and hub_verify_token == expected_token:
        logger.info("[WhatsApp Webhook] Verification successful!")
        return Response(content=hub_challenge, media_type="text/plain", status_code=200)

    logger.warning(f"[WhatsApp Webhook] Verification failed. Received token: '{hub_verify_token}', expected: '{expected_token}'")
    raise HTTPException(status_code=403, detail="Verification token mismatch")


@router.post("/webhook")
async def handle_webhook(request: Request, db: Session = Depends(get_db)):
    """
    POST /webhook endpoint receiving incoming WhatsApp message events from Meta.
    """
    try:
        payload = await request.json()
    except Exception:
        # Invalid JSON or empty body - return 200 OK so Meta does not retry endlessly
        return {"status": "ignored"}

    parsed_msg = whatsapp_service.extract_incoming_message(payload)
    if not parsed_msg:
        # Event is a status delivery receipt or non-text message
        return {"status": "ok"}

    sender_phone = parsed_msg["from_number"]
    message_text = parsed_msg["text"]
    message_id = parsed_msg.get("message_id")

    logger.info(f"[WhatsApp Inbound] Message from {sender_phone}: '{message_text}'")

    # Mark message as read on WhatsApp
    if message_id:
        whatsapp_service.mark_message_as_read(message_id)

    # Process message using existing AI Case Worker Service
    try:
        ai_res = ai_case_worker.analyze_and_respond(message_text, db)
        reply_text = ai_res.get("reply", "")

        # Append formatted matched schemes details if any schemes were matched
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

        # Send response text back to citizen's WhatsApp number
        whatsapp_service.send_text_message(sender_phone, reply_text)

    except Exception as err:
        logger.error(f"[WhatsApp Webhook] Error invoking AI Case Worker: {err}")
        # Send friendly error response
        whatsapp_service.send_text_message(
            sender_phone,
            "Namaste! JanSathi AI system is currently processing your request. Please try again shortly."
        )

    return {"status": "ok"}
