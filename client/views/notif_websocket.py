from fastapi import APIRouter
from starlette.websockets import WebSocket, WebSocketDisconnect

from websocket.manager import connection_manager

router = APIRouter()


@router.websocket("/ws/{uid}")
async def websocket_endpoint(
    *,
    websocket: WebSocket,
    uid: str,
):
    await connection_manager.connect(websocket, uid)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connection_manager.disconnect(uid)
