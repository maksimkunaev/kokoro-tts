from kokoro import KPipeline
import soundfile as sf
import torch
import os

# Change working directory to the script's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("Initializing Kokoro pipeline...")
pipeline = KPipeline(lang_code="a")

text = """
Kokoro is an open-weight TTS model with 82 million parameters. Despite its lightweight architecture, it delivers comparable quality to larger models while being significantly faster and more cost-efficient. With Apache-licensed weights, Kokoro can be deployed anywhere from production environments to personal projects.
"""

print("Generating audio...")
generator = pipeline(text, voice="bf_emma", speed=1, split_pattern=r"\n+")

for i, (gs, ps, audio) in enumerate(generator):
    filename = f"output_{i}.wav"
    sf.write(filename, audio, 24000)
    print(f"Generated {filename} for text: {gs[:50]}...")

print("Done!")
