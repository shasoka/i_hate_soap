from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, uid: str):
        await websocket.accept()
        self.active_connections[uid] = websocket

    async def disconnect(self, websocket: WebSocket, uid: str):
        await websocket.close()
        if uid in self.active_connections:
            del self.active_connections[uid]


connection_manager = ConnectionManager()
