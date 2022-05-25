from dataclasses import dataclass
from typing import Final, NewType, Tuple, cast

Account = NewType('Account', str) # NATS account
ServiceName = NewType('ServiceName', str) # (ie. 'pricing_server')
InstanceName = NewType('InstanceName', str) # (ie. '#3')

ServerId = NewType('ServerId', str) # UUID of the server, renewed each launch
SessionId = NewType('SessionId', str) # terminal segment of the dedicated subject of a session (name of peer + UUID)

FQ_INSTANCE_SEPARATOR: Final[str] = '/'

@dataclass
class FullyQualifiedInstanceName:
    account: Account
    service: ServiceName
    instance: InstanceName

    def format(self) -> str:
        return FQ_INSTANCE_SEPARATOR.join((self.account, self.service, self.instance))

    @classmethod
    def parse(cls, formatted: str) -> 'FullyQualifiedInstanceName':
        return cls(*cast(Tuple[Account, ServiceName, InstanceName], formatted.split(FQ_INSTANCE_SEPARATOR, 2)))
