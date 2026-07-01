import asyncio
import json
import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from agent.asr import transcribe_audio
from agent.brain import process_query
from render.tts import generate_speech_stream
from render.musetalk import generate_video_frames
from db.neon_client import save_chat_history

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

    async def run_pipeline(transcript: str):
        try:
            full_reply = ""
            async for event in process_query(session_id, transcript):
                if event["type"] == "widget":
                    await safe_send_json(event)
                    continue

                # event["type"] == "text"
                full_reply += event["content"]
                await safe_send_json(event)

                # Buffering strategy: MuseTalk needs a full audio buffer per
                # call (it isn't a true streaming model), so we buffer TTS
                # output per SENTENCE CHUNK — i.e. per event yielded by the
                # agent — rather than per raw TTS packet, and per the whole
                # reply. This keeps latency low (video starts after the
                # first sentence, not the whole answer) while still giving
                # MuseTalk a coherent chunk of audio to lip-sync against.
                tts_buffer = bytearray()
                async for audio_chunk in generate_speech_stream(event["content"]):
                    tts_buffer.extend(audio_chunk)

                async for video_frame in generate_video_frames(bytes(tts_buffer)):
                    await safe_send_bytes(video_frame)

            await save_chat_history(session_id, "user", transcript)
            if full_reply:
                await save_chat_history(session_id, "assistant", full_reply)

        except Exception as exc:
            await safe_send_json({"type": "error", "content": str(exc)})

    await safe_send_json({"type": "session", "session_id": session_id})

    try:
        while True:
            data = await websocket.receive()

            if data.get("bytes") is not None:
                audio_buffer.extend(data["bytes"])

            elif data.get("text") is not None:
                msg = json.loads(data["text"])

                if msg.get("type") == "end_of_turn":
                    if audio_buffer:
                        pending_audio = bytes(audio_buffer)
                        audio_buffer.clear()
                        transcript = await transcribe_audio(pending_audio)
                        if transcript:
                            asyncio.create_task(run_pipeline(transcript))

                elif msg.get("type") == "chat":
                    content = msg.get("content", "").strip()
                    if content:
                        asyncio.create_task(run_pipeline(content))

    except WebSocketDisconnect:
        print(f"Client disconnected: {session_id}")
