# Kokoro TTS Server

A small FastAPI server that turns text into speech with the open-weight [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) model and streams the audio back as WAV. Ships with a Dockerfile.

<!-- Add a screenshot or GIF here: docs/screenshot.png -->

## What it does

- Loads a Kokoro pipeline (American English, `lang_code='a'`) once at startup.
- `POST /tts` takes text, a voice name and a speed, and streams a single WAV response (24 kHz, mono, 16-bit PCM) while the model is still generating later sentences.
- `GET /health` returns a simple status payload.
- `test_tts.py` is a standalone script that generates sample `output_N.wav` files without the server.

## Tech stack

- Python, FastAPI, Uvicorn
- [kokoro](https://pypi.org/project/kokoro/) (Kokoro-82M) on PyTorch
- soundfile / libsndfile for audio encoding
- espeak-ng (system package, used by Kokoro's phonemizer)
- Docker (`python:3.12-slim` base image)

## Getting started

### With Docker

```bash
docker build -t kokoro-tts .
docker run --rm -p 5000:5000 kokoro-tts
```

The image build downloads the model weights from Hugging Face, so the container starts quickly afterwards.

### Locally

Requires Python 3.12 (as in the Dockerfile) and the system packages `espeak-ng` and `libsndfile1` (Debian/Ubuntu names).

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python server.py
```

The first start downloads the model weights from Hugging Face.

### Configuration

Optional environment variables (see `.env.example`):

| Name   | Default   | Purpose                  |
|--------|-----------|--------------------------|
| `HOST` | `0.0.0.0` | Interface Uvicorn binds  |
| `PORT` | `5000`    | Port Uvicorn listens on  |

## API

### `POST /tts`

JSON body:

| Field   | Type   | Default    |
|---------|--------|------------|
| `text`  | string | required   |
| `voice` | string | `af_heart` |
| `speed` | float  | `1.0`      |

Example:

```bash
curl -X POST http://localhost:5000/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello from Kokoro.", "voice": "af_heart", "speed": 1.0}' \
  --output speech.wav
```

Because the response is streamed, the WAV header uses "unknown length" size fields. Most players (browsers, ffmpeg, VLC, soundfile) handle this.

Voices: the pipeline is set up for American English, so the American voices (names starting with `af_` / `am_`) fit best. The full list is in the model's [VOICES.md](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md).

### `GET /health`

```bash
curl http://localhost:5000/health
# {"status":"ok","model":"Kokoro-82M"}
```

## Project structure

```
.
├── server.py          # FastAPI app: /tts (streaming WAV) and /health
├── test_tts.py        # Standalone script that writes output_N.wav samples
├── requirements.txt   # Python dependencies
├── Dockerfile         # Image with espeak-ng, libsndfile and pre-downloaded weights
└── .env.example       # Optional HOST / PORT overrides
```

## Known issues

- No authentication and no limit on text length. Do not expose the server publicly as-is; long inputs can tie up CPU/GPU.
- Only one language pipeline (American English) is loaded.
- Dependency versions are not pinned (only `kokoro>=0.9.2`).

## License

Code in this repository is MIT licensed, see [LICENSE](LICENSE). The Kokoro-82M model weights are distributed under their own license (Apache 2.0, per the model card).
