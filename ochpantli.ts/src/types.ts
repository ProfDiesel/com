export type ServiceName = string;
export type ServerName = string;
export type ClientConnectionId = number;
export type ClientConnectionName = string;


export interface ClientConnection {
  server: ServerName;
  id: ClientConnectionId;
  name: ClientConnectionName;
}
