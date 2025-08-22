from fastapi import APIRouter, WebSocket

router = APIRouter()

@router.websocket('/runs/{run_id}/events')
async def events_ws(websocket: WebSocket, run_id: str):
    await websocket.accept()
    await websocket.send_json({"run_id": run_id, "event": "placeholder"})
    await websocket.close()
