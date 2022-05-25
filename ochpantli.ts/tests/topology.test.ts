import {ConnectionManager } from "../src/monitoring/ConnectionManager"
import { NatsConnection, connect, JSONCodec, Msg, Subscription } from 'nats.ws';
import { Topology, TopologyClient } from '../src/services/TopologyService';

import { configureStore, ThunkAction, Action, Store } from '@reduxjs/toolkit';
import componentListReducer from '../src/monitoring/ComponentListSlice';

import usePromise from '../src/misc/usePromise';

export const store = configureStore({
  reducer: {
    componentList: componentListReducer,
  },
});

export type AppDispatch = typeof store.dispatch;
export type RootState = ReturnType<typeof store.getState>;
export type AppThunk<ReturnType = void> = ThunkAction<ReturnType, RootState, unknown, Action<string>>;


export class DuctTape {
  natsClient?: NatsConnection;
  topologyClient?: TopologyClient;
  connectionManager?: ConnectionManager;

  constructor(private natsUrl: string, private realm: string, private instance: string) {}

  async connect() {
    this.natsClient = await connect({ servers: this.natsUrl });
    this.topologyClient = new TopologyClient(this.natsClient, this.realm, this.instance);
    const topology: Topology = await this.topologyClient.get_topology();
    this.connectionManager = new ConnectionManager(store, this.natsClient, topology);
  }
}

test("Dummy unit test", () => {
  const ductTape = new DuctTape('localhost:4222', 'realm', 'instance');
  const { value, loading } = usePromise<void>(ductTape.connect);
  expect(0).toBe(0);
});
