import edge_tts
from typing import AsyncGenerator

async def generate_speech_stream(text: str) -> AsyncGenerator[bytes, None]:
    """Streams audio chunks in real-time as they are generated to minimize latency."""
    communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            yield chunk["data"]
