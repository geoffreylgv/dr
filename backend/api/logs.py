from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..ws_manager import WSManager
from ..docker_client import DockerClient

router = APIRouter()
_manager = WSManager(DockerClient())


@router.websocket("/ws/logs/{container_id}")
async def log_stream(container_id: str, ws: WebSocket):
    await _manager.connect(container_id, ws)
    try:
        while True:
            await ws.receive_text()  # keep alive; client sends nothing meaningful
    except WebSocketDisconnect:
        _manager.disconnect(container_id, ws)
