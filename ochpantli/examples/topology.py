import asyncio

import nats
from nats.aio.client import Client as NatsClient
from pydantic_yaml import YamlModel

from com.com import Server
from com.services.topology import Topology, TopologyServer


class Model(YamlModel):
    queue: str
    topology: Topology


class TopologyServerImpl(Server, protos=(TopologyServer,)):
    def __init__(self, nc: NatsClient, model: Model):
        super().__init__(nc)
        self.__model = model

    async def get_topology(self) -> Topology:
        return self.__model.topology

    async def run(self):
        await self.sub('TopologyServer', queue=self.__model.queue)


async def main():
    nc = await nats.connect('nats://a:a@localhost:4222')
    topo_server: TopologyServerImpl = TopologyServerImpl(nc, Model.parse_file('topology.yaml'))

    subs = [asyncio.create_task(topo_server.run()),]
    await asyncio.gather(*subs)

    await nc.close()

if __name__ == '__main__':
    asyncio.run(main())
