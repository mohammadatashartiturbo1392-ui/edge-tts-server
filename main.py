from fastapi import FastAPI, Query
from fastapi.responses import Response, JSONResponse
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
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=rate
        )
        
        # ✅ همه chunks رو جمع کن
        audio_chunks = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_chunks.append(chunk["data"])
        
        if not audio_chunks:
            return JSONResponse(
                {"error": "no audio chunks received"},
                status_code=500
            )
        
        # ✅ یکی کن
        audio_data = b"".join(audio_chunks)
        print(f"✅ Audio: {len(audio_data)} bytes | text: {text[:30]}")
        
        # ✅ Response مستقیم با bytes
        return Response(
            content=audio_data,
            media_type="audio/mpeg",
            headers={
                "Content-Length": str(len(audio_data)),
                "Cache-Control": "no-cache",
                "Access-Control-Allow-Origin": "*"
            }
        )
        
    except Exception as e:
        err = traceback.format_exc()
        print(f"❌ Error: {err}")
        return JSONResponse(
            {"error": str(e), "detail": err[-300:]},
            status_code=500
        )
