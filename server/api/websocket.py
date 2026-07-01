import asyncio
import json
import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = str(uuid.uuid4())
    send_lock = asyncio.Lock()
    audio_buffer = bytearray()

    async def safe_send_json(payload: dict):
        async with send_lock:
            await websocket.send_json(payload)

    async def safe_send_bytes(payload: bytes):
        async with send_lock:
            await websocket.send_bytes(payload)

    await safe_send_json({"type": "session", "session_id": session_id})

    try:
        while True:
            data = await websocket.receive()

            if data.get("bytes") is not None:
                audio_buffer.extend(data["bytes"])

            elif data.get("text") is not None:
                msg = json.loads(data["text"])
                # TODO(Task 4): route "end_of_turn" -> ASR -> agent -> TTS -> MuseTalk
                # TODO(Task 4): route "chat" -> agent -> TTS -> MuseTalk
                await safe_send_json({
                    "type": "chat",
                    "content": f"[session {session_id[:8]}] received: {msg.get('type')}",
                })

    except WebSocketDisconnect:
        print(f"Client disconnected: {session_id}")
