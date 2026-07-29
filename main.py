from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse, JSONResponse
import edge_tts
import asyncio
import io

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "service": "Edge-TTS - Mohammad Ata"}

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
        buf.seek(0)
        if buf.getbuffer().nbytes < 100:
            return JSONResponse({"error": "empty audio"}, status_code=500)
        return StreamingResponse(buf, media_type="audio/mpeg")
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
