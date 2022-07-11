import { createSlice, PayloadAction } from '@reduxjs/toolkit';
// @ts-ignore
import { ClientConnection, ServiceName } from '../types.ts';
// @ts-ignore
import { Immutable } from '../misc/Immutable.ts';
/* // eslint-disable-next-line node/no-extraneous-import */
import { Draft } from 'immer';

export interface ClientConnectionOnService {
  service: ServiceName;
  connection: ClientConnection;
}

export interface ComponentState {
  name: ServiceName;
  clientConnections: Set<ClientConnection>;
}

export interface ComponentListState {
  components: Map<ServiceName, ComponentState>;
}

const initialState: ComponentListState = {
  components: new Map(),
};

export const componentListSlice = createSlice({
  name: 'componentList',
  initialState,
  reducers: {
    addConnection: (state: Draft<ComponentListState>, action: Immutable<PayloadAction<ClientConnectionOnService>>): void => {
      state.components.get(action.payload.service)?.clientConnections.add(action.payload.connection);
    },
    removeConnection: (state: Draft<ComponentListState>, action: Immutable<PayloadAction<ClientConnectionOnService>>): void => {
      state.components.get(action.payload.service)?.clientConnections.delete(action.payload.connection);
    },
    setConnections: (state: Draft<ComponentListState>, action: PayloadAction<Iterable<ClientConnectionOnService>>): void => {
      for (const it of state.components.values()) {
        it.clientConnections.clear();
      }
      for (const it of action.payload) {
        state.components.get(it.service)?.clientConnections.add(it.connection);
      }
    },
    setServiceList: (state: Draft<ComponentListState>, action: PayloadAction<Iterable<ServiceName>>) => {
      state.components = new Map([...action.payload].map((serviceName) => [serviceName, state.components.get(serviceName) ?? ({ name: serviceName, clientConnections: new Set() } as ComponentState)]));
    },
  },
});

export const { addConnection, removeConnection, setConnections, setServiceList } = componentListSlice.actions;
export default componentListSlice.reducer;
