from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from kokoro import KPipeline
import io
import soundfile as sf
import time
import torch
import numpy as np

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

def generate_audio_chunks(text: str, voice: str, speed: float):
    """Generator that yields audio chunks as bytes."""
    generator = pipeline(text, voice=voice, speed=speed)
    for i, (gs, ps, audio) in enumerate(generator):
        # Convert numpy array to WAV bytes
        buffer = io.BytesIO()
        sf.write(buffer, audio, 24000, format='WAV')
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
    # Use port 5000 as requested
    uvicorn.run(app, host="0.0.0.0", port=5000)
