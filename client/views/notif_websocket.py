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

    while True:
        try:
            await websocket.receive_json()
        except WebSocketDisconnect:
            try:
                await connection_manager.disconnect(websocket, uid)
            finally:
                break
