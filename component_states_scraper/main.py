from datetime import datetime
from types import SimpleNamespace
from typing import cast, Dict
from urllib import request
from com.service.topology import Topology
from com.types import Account, FullyQualifiedInstanceName
import requests
from nats.aio.client import Client as NatsClient
from nats.aio.msg import Msg
from functools import partial


import json

class Config:
    topology_json_url: str # from S3 ?

class Event:
    json: SimpleNamespace

    @property
    def account(self) -> Account:
        return cast(Account, self.json.client.acc)

    @property
    def timestamp(self) -> datetime:
        return datetime.fromisoformat(self.json.timestamp)


class Status:
    last_connect: Event
    last_disconnect: Event

statuses: Dict[FullyQualifiedInstanceName, Status]

async def on_connect(account: Account, msg: Msg):
    """$> nats schema info io.nats.server.advisory.v1.client_connect"""
    event = json.load(msg.data)
    if not event.type == 'io.nats.server.advisory.v1.client_connect':
        return
    statuses[getFQIN(msg)].last_connect = Event(json=event)

def get_topology(config: Config) -> Topology:
    return Topology.parse_obj(requests.get(config.topology_json_url).json)

async def subscribe_to_events(topology: Topology, client: NatsClient):
    for account in topology.accounts:
        await client.subscribe('$SYS.ACCOUNT.{account}.CONNECT', cb=partial(on_connect, account=account))
        await client.subscribe('$SYS.ACCOUNT.{account}.DISCONNECT', cb=partial(on_disconnect, account=account)

async def snapshot(client: NatsClient):
    result = await client.request('$SYS.REQ.SERVER.PING.CONNZ')
    result.
""""
  async snapshot(): Promise<void> {
    const pingResponse: Msg = await this.nats_client.request('$SYS.REQ.SERVER.PING.CONNZ');
    const data: unknown = ConnectionManager.CODEC.decode(pingResponse.data);
    const {
      server: { name: server_name, connections },
    } = data as { server: { name: string; connections: Array<{ cid: number; name: string }> } };
    this.store.dispatch(setConnections(connections.map((connection) => { return { service: ConnectionManager.extractServiceName(connection.name), connection: { server: server_name, id: connection.cid, name: connection.name } } as ClientConnectionOnService} )))
  }
"""
# connecte aux evenements $SYS de NATS
# périodiquement (5 min ?), ping global
