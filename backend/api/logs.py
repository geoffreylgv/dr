from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request

router = APIRouter()


@router.websocket("/ws/logs/{container_id}")
async def log_stream(container_id: str, ws: WebSocket, request: Request):
    manager = request.app.state.ws_manager
    await manager.connect(container_id, ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(container_id, ws)
