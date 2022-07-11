// Generated code - DO NOT EDIT

// @ts-ignore
import { Request, Response, Client } from '../Common.ts';




export type Account = string


export type ServiceName = string


export type InstanceName = string


export interface FullyQualifiedInstanceName {
  account:  Account;
  service:  ServiceName;
  instance:  InstanceName;
}


export type FullyQualifiedInstanceNameList = Array<FullyQualifiedInstanceName>

export type AccountList = Array<Account>

export interface Topology {
  instances:  FullyQualifiedInstanceNameList;
  accounts:  AccountList;
}





//
// service Topology


// method get_topology
interface GetTopologyRequest extends Request {
}
interface GetTopologyResponse extends Response {
  value: Topology;
}

export class TopologyClient extends Client {
  get service(): string { return 'Topology'; }
  async get_topology(): Promise<Topology> {
    return ((await super.request({ type: 'get_topology',  } as GetTopologyRequest)) as GetTopologyResponse).value;
  }
}
