from io import BytesIO
from operator import imod
from typing import Optional, Any
from aioboto3 import Session
from nats.aio.client import Client as NatsClient
from ..com import encode as default_encode, decode as default_decode, decode_stream
from aiohttp import ClientSession
from dataclasses import dataclass

@dataclass
class BigMessage:
    payload: Optional[Any]
    url: Optional[str]

class Server:
    MARGIN = 128

    VIRTUAL_HOST_URL_FORMAT = 'https://{bucket}.s3.amazonaws.com/{key}'
    PATH_STYLE_FORMAT = 'https://s3.eu-central-1.amazonaws.com/{bucket}/{key}'

    def __init__(self, client: NatsClient, bucket: str, url_format: str = PATH_STYLE_FORMAT):
        self.__bucket = bucket
        self.__max_payload = client.max_payload - self.MARGIN
        self.__url_format = url_format

    async def encode(self, payload: Any, reply_subject: str) -> bytes:
        if len(payload) >= self.__max_payload:
            session = Session()
            async with session.client('s3') as s3:
                await s3.upload_fileobj(BytesIO(payload), self.__bucket, reply_subject)
            return default_encode(BigMessage(url=self.__url_format.format(bucket = self.__bucket, key = reply_subject)))

        return default_encode(BigMessage(payload = payload))

class Client:
    async def decode_reply(self, payload: bytes) -> bytes:
        message: BigMessage = default_decode(payload)
        if message.payload:
            return message.payload
        async with ClientSession as session:
            async with session.get(message.url) as response:
                # TODO: stream this ?
                return default_decode(response.content)
