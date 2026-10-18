import io
import os
import struct

import soundfile as sf
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from kokoro import KPipeline
from pydantic import BaseModel

SAMPLE_RATE = 24000
CHANNELS = 1
BITS_PER_SAMPLE = 16

app = FastAPI(title="Kokoro TTS API")

# Pre-load the pipeline
print("Loading Kokoro pipeline...")
pipeline = KPipeline(lang_code='a')


class TTSRequest(BaseModel):
    text: str
    voice: str = 'af_heart'
    speed: float = 1.0


@app.get("/health")
async def health():
    return {"status": "ok", "model": "Kokoro-82M"}


def wav_stream_header() -> bytes:
    """WAV header for a stream of unknown length (sizes set to the max value)."""
    byte_rate = SAMPLE_RATE * CHANNELS * BITS_PER_SAMPLE // 8
    block_align = CHANNELS * BITS_PER_SAMPLE // 8
    unknown_size = 0xFFFFFFFF
    return (
        b"RIFF" + struct.pack("<I", unknown_size) + b"WAVE"
        + b"fmt " + struct.pack("<IHHIIHH", 16, 1, CHANNELS, SAMPLE_RATE,
                                byte_rate, block_align, BITS_PER_SAMPLE)
        + b"data" + struct.pack("<I", unknown_size)
    )


def generate_audio_chunks(text: str, voice: str, speed: float):
    """Generator that yields one WAV header followed by raw 16-bit PCM chunks."""
    yield wav_stream_header()
    generator = pipeline(text, voice=voice, speed=speed)
    for _graphemes, _phonemes, audio in generator:
        if audio is None:
            continue
        buffer = io.BytesIO()
        sf.write(buffer, audio, SAMPLE_RATE, format='RAW', subtype='PCM_16')
        yield buffer.getvalue()


@app.post("/tts")
async def generate_tts(request: TTSRequest):
    print(f"Generating TTS (Streaming) for: {request.text[:50]}...")

    # For small texts, streaming might be overkill, but it provides the lowest latency
    return StreamingResponse(
        generate_audio_chunks(request.text, request.voice, request.speed),
        media_type="audio/wav"
    )


if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("HOST") or "0.0.0.0"
    port = int(os.environ.get("PORT") or "5000")
    uvicorn.run(app, host=host, port=port)
