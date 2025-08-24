from fastapi import APIRouter, WebSocket

EVENT_TYPES = {"FEATURES_READY", "BACKTEST_FINISHED"}

router = APIRouter()


@router.websocket('/runs/{run_id}/events')
async def events_ws(websocket: WebSocket, run_id: str) -> None:
    await websocket.accept()
    # Eventos fictícios apenas para ilustração
    for event in EVENT_TYPES:
        await websocket.send_json({"run_id": run_id, "event": event})
    await websocket.close()
