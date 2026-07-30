from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse, JSONResponse
import edge_tts
import asyncio
import io
import traceback

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "service": "Edge-TTS - Mohammad Ata"}

@app.get("/ping")
def ping():
    return {"pong": True}

@app.get("/test")
async def test():
    try:
        communicate = edge_tts.Communicate(text="hello", voice="en-US-AriaNeural")
        buf = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                buf.write(chunk["data"])
        size = buf.getbuffer().nbytes
        return {"status": "ok", "size": size}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/tts")
async def tts(
    text: str = Query(...),
    voice: str = Query(default="fa-IR-FaridNeural"),
    rate: str = Query(default="+0%")
):
    try:
        communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
        buf = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                buf.write(chunk["data"])
        size = buf.getbuffer().nbytes
        print(f"Audio size: {size} for: {text[:30]}")
        if size < 100:
            return JSONResponse({"error": "empty", "size": size}, status_code=500)
        buf.seek(0)
        return StreamingResponse(
            buf, media_type="audio/mpeg",
            headers={"Content-Length": str(size)}
        )
    except Exception as e:
        print(traceback.format_exc())
        return JSONResponse({"error": str(e)}, status_code=500)
