export interface JSONMessage {
    Type: string;
}

export interface JSONLoginKeyElements {
    ApplicationId: string;
    Position: string;
}

export interface JSONLoginKey {
    Elements: JSONLoginKeyElements;
    Name: string;
}

export interface JSONLogin {
    ID: number;
    Domain: "Login";
    Key: JSONLoginKey;
}

export function login(id: number,
    name: string,
    applicationId: string,
    position: string,
): JSONLogin {
    return {
        ID: id, Domain: "Login", Key: {
            Elements: {
                ApplicationId: applicationId, Position: position
            },
            Name: name
        }
    }
}

export interface JSONItemRequestKey {
    Name: string | Array<string>;
    Service?: string;
}

export interface JSONItemRequestMsg {
    ID: number;
    Key: JSONItemRequestKey;
    View?: Array<String>
}

export function requestItem(id: number, name: string, service: string): JSONItemRequestMsg {
    return {
        ID: id, Key: {
            Name: name,
            Service: service
        }
    }
}

export interface JSONClose {
    Domain?: string;
    ID: number;
    Type: "Close";
}

export function close(id: number): JSONClose {
    return { ID: id, Type: "Close" }
}

export function closeLogin(id: number): JSONClose {
    return { Domain: "Login", ID: id, Type: "Close" }
}
