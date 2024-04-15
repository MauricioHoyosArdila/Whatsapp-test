from dotenv import load_dotenv

from fastapi import APIRouter, Request
from ..services.openia_service import generate_manychat_response


router = APIRouter()
load_dotenv()


@router.post("/receive_message_from_manychat")
async def manychatMessage(request: Request):
    body = await request.json()
    print(body)
    response = generate_manychat_response(body['ultima_respuesta'], body['thread_id'])
    return response
