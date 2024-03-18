import logging
import json
import os
from dotenv import load_dotenv

from fastapi import APIRouter, Request, Response

from ..decorators.security import signature_required
from ..utils.whatsapp_utils import (
    process_whatsapp_message,
    is_valid_whatsapp_message,
)

router = APIRouter()
load_dotenv()


async def handle_message(request):
    """
    Handle incoming webhook events from the WhatsApp API.

    This function processes incoming WhatsApp messages and other events,
    such as delivery statuses. If the event is a valid message, it gets
    processed. If the incoming payload is not a recognized WhatsApp event,
    an error is returned.

    Every message send will trigger 4 HTTP requests to your webhook: message, sent, delivered, read.

    Returns:
        response: A tuple containing a JSON response and an HTTP status code.
    """
    body = await request.json()
    # logging.info(f"request body: {body}")

    # Check if it's a WhatsApp status update
    if (
        body.get("entry", [{}])[0]
        .get("changes", [{}])[0]
        .get("value", {})
        .get("statuses")
    ):
        logging.info("Received a WhatsApp status update.")
        return {"status": "ok"}, 200

    try:
        if is_valid_whatsapp_message(body):
            process_whatsapp_message(body)
            return {"status": "ok"}, 200
        else:
            # if the request is not a WhatsApp API event, return an error
            return {"status": "error", "message": "Not a WhatsApp API evnt"}, 404
    except json.JSONDecodeError:
        logging.error("Failed to decode JSON")
        return {"status": "error", "message": "Invalid JSON provided"}, 400


# Required webhook verifictaion for WhatsApp
async def verify(request):
    # Parse params from the webhook verification request
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    print(mode, " ", token, " ", challenge, " ", os.getenv("VERIFY_TOKEN"))
    # Check if a token and mode were sent
    if mode and token:
        # Check the mode and token sent are correct
        if mode == "subscribe" and token == os.getenv("VERIFY_TOKEN"):
            # Respond with 200 OK and challenge token from the request
            logging.info("WEBHOOK_VERIFIED")
            print(challenge)
            return Response(content=challenge, status_code=200)
        else:
            # Responds with '403 Forbidden' if verify tokens do not match
            logging.info("VERIFICATION_FAILED")
            return {"status": "error", "message": "Verification failed"}, 403
    else:
        # Responds with '400 Bad Request' if verify tokens do not match
        logging.info("MISSING_PARAMETER")
        return {"status": "error", "message": "Missing parameters"}, 400


@router.get("/webhook")
async def webhook_get(request: Request):
    print(request)
    response = await verify(request)
    print(response)
    return response


@router.post("/webhook")
@signature_required
async def webhook_post(request: Request):
    return await handle_message(request)
