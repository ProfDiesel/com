from abc import abstractmethod, abstractproperty
from dataclasses import dataclass
from http import server
from typing import Final, NewType, Protocol, Tuple, TypeVar, Optional

from nats.aio.client import Client

from ..magic import ServerImpl, client, server
from .types import FullyQualifiedInstanceName, ServerId, SessionId
from nats.nuid import NUID

@dataclass
class FullyQualifiedSessionId:
    server_name: FullyQualifiedInstanceName
    server_id: ServerId
    session_id: SessionId

    def is_new_session(self, server_name: FullyQualifiedInstanceName, server_id: ServerId) -> bool:
        return (server_name == self.server_name) and (server_id != self.server_id)

@dataclass
class LoginResponse:
    ok: bool
    reason: str
    session: FullyQualifiedSessionId

class LoginFailedError(Exception):
    def __init__(self, response: LoginResponse):
        self.response: Final[LoginResponse] = response

@server
class HomeServer(Protocol):
    async def login(self, credentials: bytes) -> LoginResponse:
        ...

@client(HomeServer)
class HomeClient(Protocol):
    async def new_server_id(server_id: ServerId) -> None:
        ...

class HomeServerImpl(ServerImpl[HomeServer]):
    def __init__(self, server_name: FullyQualifiedInstanceName):
        self.__nuid: Final[NUID] = NUID()
        self.__server_name: Final[FullyQualifiedInstanceName] = server_name
        self.__server_id: ServerId = ServerId()

    def __generate_id(self) -> ServerId:
        return self.__nuid.next().decode()

    async def connect(self):
        self.__server_id = self.__generate_id()

    async def login(self, credentials: bytes) -> LoginResponse:
        return LoginResponse(True, '', self.__server_id)

    async def __startup_procedure(self):
        self.multicast_clients.new_server_id(self.__server_name, self.__server_id) # publish the new server_id, every client to re-connect if the server is re-launching


class HomeClientImpl:
    @abstractproperty
    def credentials(self) -> bytes:
        raise NotImplementedError()

    def __init__(self, server: HomeServer):
        self.__server: Final[HomeServer] = server
        self.__session_id: Optional[SessionId] = None

    async def connect(self):
        response: Final[LoginResponse] = self.__server.login(credentials=self.credentials)
        if not response.ok:
            raise LoginFailedError(response)
        self.__session_id = response.session;

    async def new_server_id(self, server_name: FullyQualifiedInstanceName, server_id: ServerId) -> None:
        if self.__session_id.is_new_session(server_name, server_id):
            self.connect(self.__server)
