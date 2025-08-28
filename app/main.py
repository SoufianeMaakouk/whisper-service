# app/main.py
import base64
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
    try:
        while True:
            # Receive audio chunk (Base64 string)
            message = await websocket.receive_text()
            audio_bytes = base64.b64decode(message)

            # Send to Whisper (streaming in chunks)
            transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_bytes
            )
            text = transcript.text

            # Send transcription back to frontend
            await websocket.send_text(text)

    except Exception as e:
        print("WebSocket error:", e)
        await websocket.close()
