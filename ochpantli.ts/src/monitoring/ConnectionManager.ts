import { NatsConnection, JSONCodec, Msg, Subscription } from 'nats.ws';
import { merge } from 'ix/asynciterable/merge';
import { Store } from 'redux'

import { ClientConnectionName, ServiceName } from '../types';
import { Topology } from '../services/TopologyService';
import { addConnection, ClientConnectionOnService, removeConnection, setConnections } from './ComponentListSlice';

export class ConnectionManager {
  static CODEC = JSONCodec();

  _subscriptions: Set<Subscription> = new Set();

  constructor(private store: Store, private nats_client: NatsConnection, private topology: Topology) {}

  static extractServiceName(connectionName: ClientConnectionName): ServiceName {
    return connectionName
  }

  async snapshot(): Promise<void> {
    const pingResponse: Msg = await this.nats_client.request('$SYS.REQ.SERVER.PING.CONNZ');
    const data: unknown = ConnectionManager.CODEC.decode(pingResponse.data);
    const {
      server: { name: server_name, connections },
    } = data as { server: { name: string; connections: Array<{ cid: number; name: string }> } };
    this.store.dispatch(setConnections(connections.map((connection) => { return { service: ConnectionManager.extractServiceName(connection.name), connection: { server: server_name, id: connection.cid, name: connection.name } } as ClientConnectionOnService} )))
  }

  async connect() {
    for (const account of this.topology.accounts) {
      this._subscriptions.add(this.nats_client.subscribe(`$SYS.ACCOUNT.${account}.CONNECT`));
      this._subscriptions.add(this.nats_client.subscribe(`$SYS.ACCOUNT.${account}.DISCONNECT`));
    }
    const subs: IterableIterator<Subscription> = this._subscriptions.values();
    for await (const message of merge(subs.next().value, ...subs)) {
      const data: unknown = ConnectionManager.CODEC.decode(message.data);
      const { type } = data as { type: string };
      if (type === 'io.nats.server.advisory.v1.client_connect') {
        const {
          server: { name: server_name },
          client: { id, name },
        } = data as { server: { name: string }; client: { id: number; name: string } };
        this.store.dispatch(addConnection({ service: ConnectionManager.extractServiceName(name), connection: { server: server_name, id: id, name: name } } as ClientConnectionOnService))
      } else if (type === 'io.nats.server.advisory.v1.client_disconnect') {
        const {
          server: { name: server_name },
          client: { id, name },
          reason,
        } = data as { server: { name: string }; client: { id: number; name: string }; reason: string };
        this.store.dispatch(removeConnection({ service: ConnectionManager.extractServiceName(name), connection: { server: server_name, id: id, name: name } } as ClientConnectionOnService))
      }
    }
  }
}
