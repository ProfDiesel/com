from typing import List, Protocol
from dataclasses import dataclass

from com import server
from com.types import Account, FullyQualifiedInstanceName

@dataclass
class Topology:
    instances: List[FullyQualifiedInstanceName]
    accounts: List[Account]

@server
class TopologyServer(Protocol):
    async def get_topology(self) -> Topology: ...
