from functools import wraps
import os
from dotenv import load_dotenv
from fastapi import Response
import logging
import hashlib
import hmac

load_dotenv()


def validate_signature(payload, signature):
    """
    Validate the incoming payload's signature against our expected signature
    """
    # Use the App Secret to hash the payload
    expected_signature = hmac.new(
        bytes(os.getenv("APP_SECRET"), "latin-1"),
        msg=payload.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()

    # Check if the signature matches
    return hmac.compare_digest(expected_signature, signature)


def signature_required(f):
    """
    Decorator to ensure that the incoming requests to our webhook are valid and signed with the correct signature.
    """

    @wraps(f)
    async def decorated_function(*args, **kwargs):
        signature = kwargs['request'].headers.get("X-Hub-Signature-256", "")[
            7:
        ]  # Removing 'sha256='
        playload = await kwargs['request'].body()
        print(playload)
        if not validate_signature(playload.decode("utf-8"), signature):
            logging.info("Signature verification failed!")
            return Response(content={"status": "error", "message": "Invalid signature"}, status_code=403)
        return await f(*args, **kwargs)

    return decorated_function
