# app/main.py
import base64
import tempfile
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import openai

openai.api_key = "<YOUR_OPENAI_API_KEY>"  # ⚠️ Replace with Railway Secret

app = FastAPI()

# Allow frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: replace with your frontend domain in production
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Whisper service running!"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    audio_buffer = bytearray()

    try:
        while True:
            # Receive base64 audio chunk from frontend
            message = await websocket.receive_text()
            audio_bytes = base64.b64decode(message)
            audio_buffer.extend(audio_bytes)

            # 🔑 For now: process when buffer is large enough
            if len(audio_buffer) > 16000 * 2 * 5:  # ~5 seconds of 16kHz PCM16
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp.write(audio_buffer)
                    tmp.flush()

                    # Send complete file to Whisper
                    with open(tmp.name, "rb") as f:
                        transcript = openai.audio.transcriptions.create(
                            model="whisper-1",
                            file=f
                        )

                    text = transcript.text
                    await websocket.send_text(text)

                # Reset buffer after sending
                audio_buffer = bytearray()

    except Exception as e:
        print("WebSocket error:", e)
        await websocket.close()
