import json
from os import environ
from asyncio import wrap_future

from fastapi import APIRouter, Depends
from pydantic import BaseModel, validator

import nsq

from .util import enforce_authentication, generate_message_id

router = APIRouter()

nsqd_addresses = []
for key, value in environ.items():
    if key.startswith('NSQD_ADDR'):
        nsqd_addresses.append(value)

nsq_writer = nsq.Writer(nsqd_addresses)


class Message(BaseModel):
    text: str

    @validator('text')
    def text_length(cls, text):
        if len(text) < 1 or len(text) > 4096:
            raise ValueError('Text length MUST vary in [1, 4096]')
        return text


@router.put('/message')
async def put_message(message: Message,
                      username: str = Depends(enforce_authentication)):
    message_id = generate_message_id()

    payload = {'id': message_id, 'sender': username, 'text': message.text}
    data = json.dumps(payload).encode('utf-8')
    await wrap_future(nsq_writer.pub('messages', data))

    return message_id
