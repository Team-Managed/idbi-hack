import asyncio
import io
from faster_whisper import WhisperModel
from pydub import AudioSegment

_model = WhisperModel("tiny", device="cpu", compute_type="int8")

def _transcribe_sync(audio_bytes: bytes) -> str:
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="webm")
    wav_io = io.BytesIO()
    audio.set_frame_rate(16000).set_channels(1).export(wav_io, format="wav")
    wav_io.seek(0)

    segments, _ = _model.transcribe(wav_io, language="en")
    return " ".join(segment.text for segment in segments).strip()

async def transcribe_audio(audio_bytes: bytes) -> str:
    # faster-whisper + pydub are blocking/CPU-bound — never await them directly
    # on the event loop, or every other connection's I/O stalls while this runs.
    return await asyncio.to_thread(_transcribe_sync, audio_bytes)
