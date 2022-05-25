import { NatsConnection, Msg } from 'nats.ws';
import { encode, decode } from '@msgpack/msgpack';

export interface Message {
  type: string;
}

export type Request = Message;

export interface Response extends Message {
  value: object;
}

export abstract class Client {
  constructor(protected nats_client: NatsConnection, protected realm: string, protected instance: string) {}

  abstract get service(): string;

  get subject(): string {
    return `${this.realm}.${this.service}`;
  }

  encode(data: Request): Uint8Array {
    return encode(data);
  }
  decode(data: Uint8Array): Response {
    return decode(data) as Response;
  }

  async request(request: Request): Promise<Response> {
    const response: Msg = await this.nats_client.request(this.subject, this.encode(request));
    return this.decode(response.data) as Response;
  }
}
