from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json, logging
from src.utils.websocket_manager import websocket_manager

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/stream")
async def websocket_endpoint(ws: WebSocket):
    await websocket_manager.connect(ws)
    try:
        while True:
            data = await ws.receive_text()
            try:
                message = json.loads(data)
            except Exception:
                message = {"type":"echo","data":data}
            if message.get("type") == "echo":
                await ws.send_text(json.dumps({"type":"echo","data":message.get("data")}))
            else:
                await ws.send_text(json.dumps({"error":"Unknown message type"}))
    except WebSocketDisconnect:
        websocket_manager.disconnect(ws)
    except Exception as e:
        logger.exception("WebSocket error: %s", e)
        await ws.close(code=1011)
