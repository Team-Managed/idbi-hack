from typing import AsyncGenerator

async def generate_video_frames(audio_buffer: bytes) -> AsyncGenerator[bytes, None]:
    # Stub for MuseTalk generation. Replace with real inference later —
    # the calling contract (bytes in, async-iterable of H.264 NAL units out)
    # is what Task 6's client depends on, so keep that signature stable.
    yield b'\x00\x00\x00\x01\x67...'  # Mock NAL unit
