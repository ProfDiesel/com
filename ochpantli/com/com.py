from functools import wraps
from inspect import BoundArguments, Signature, signature
from io import BytesIO
from typing import Any, Callable, Collection, Final, Optional, Type, TypeVar
from xdrlib import Unpacker

import msgpack
from nats.aio.client import Client as NatsClient
from nats.aio.subscription import Subscription

from .utils import member_functions

# from typing_extensions import

T0 = TypeVar('T0')
T = TypeVar('T')


def server(cls: Type[T]) -> Type[T]:
    cls._client_cls = None
    return cls

def client(server_cls: Type[T0]) -> Callable[[Type[T]], Type[T]]:
    def closure(cls: Type[T]) -> Type[T]:
        cls._server_cls = server_cls
        assert(server_cls._client_cls is None)
        server_cls._client_cls = cls
        return cls
    return closure


def encode(data: Any) -> bytes:
    return msgpack.packb(data)

def decode(data: bytes) -> Any:
    return msgpack.unpackb(data, use_list=False)

def decode_stream(data: BytesIO) -> Unpacker:
    return msgpack.Unpacker(data, use_list=False)


class Server:
    _METHODS = {}

    def __init_subclass__(cls, protos: Collection[Type[Any]]) -> None:
        cls._METHODS.update({name: method for proto in protos for name, method in member_functions(proto).items()})

    def __init__(self, client: NatsClient):
        self.__client: Final[NatsClient] = client

    async def sub(self, subject: str, queue: Optional[str]):
        sub: Final[Subscription] = await self.__client.subscribe(subject, queue=queue)
        async for msg in sub.messages:
            data: Any = self.decode(msg.data)
            result: Any = self._METHODS[data.pop('type')](**data)
            if msg.reply:
                self.__client.publish(msg.reply, encode(result))


class Client:
    _METHODS = {}

    @classmethod
    def remote_call(cls, func: Callable[..., Any]):
        sig: Final[Signature] = signature(func)
        has_result: Final[bool] = sig.return_annotation is not None
        @wraps(func)
        def wrapper(self, *args: Any, **kwargs: Any) -> Any:
            bound: Final[BoundArguments] = sig.bind(self, *args, **kwargs)
            bound.apply_defaults()
            request: Final[Any] = encode({'type': func.__name__, **bound.arguments})
            if has_result:
                result_struct: Final[Any] = decode(self.__client.request(self.__subject, request))
                return result_struct
            else:
                self.__client.pub(self.__subject, request)
        return wrapper

    def __init_subclass__(cls, protos: Collection[Type[Any]]) -> None:
        cls._METHODS.update({method.name: cls.remote_call(method) for proto in protos for method in member_functions(proto)})

    def __init__(self, client: NatsClient):
        self.__client: Final[NatsClient] = client
