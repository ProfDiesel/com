import { login, requestItem, close, JSONMessage } from "./messages"
import { WebsocketBuilder, ExponentialBackoff, TimeBuffer } from 'websocket-ts';

function connect(url: string): void {
  const logEvent = (ws: WebSocket, event: any) => { console.log(event) }

  const ws = new WebsocketBuilder()
    .onOpen(onOpen)
    .onClose(logEvent)
    .onError(logEvent)
    .onMessage(onMessage)
    .onRetry(logEvent)
    .withBackoff(new ExponentialBackoff(100, 7))
    .withBuffer(new TimeBuffer(5 * 60 * 1000))
    .build();
}

//An event listener to be called when a message is received from the server
function onOpen(ws: WebSocket, event: any): void {
  // (re-)send login request
  ws.send(JSON.stringify(login(loginID, username, "777", "127.0.0.1")));
}

function onMessage(ws: WebSocket, event: any): void {
  //console.log(JSON.stringify(event.data));

  let messages = JSON.parse(event.data.toString()) as Array<JSONMessage>
  messages.forEach((msg: JSONMessage) => {
    switch (msg.Type) {
      case "Ping":
        ws.send(JSON.stringify({ Type: "Pong" }));
        break;
      case "Refresh":
        if (msg?.Name == itemname)
          ;
        if (msg?.Domain == "Login")
          // subscribe
          ;
        break;

      default:
        break;
    }
  })
}
