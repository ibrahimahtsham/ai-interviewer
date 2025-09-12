#!/usr/bin/env python3
import asyncio, json, time, os
import numpy as np
import websockets
from faster_whisper import WhisperModel

MODEL_NAME = os.getenv("WHISPER_MODEL", "tiny.en")  # small English-only model
COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE", "int8")  # good for CPU-only
PORT = int(os.getenv("STT_PORT", "8765"))

SAMPLE_RATE = 16000
SAMPLE_WIDTH = 2  # bytes per sample (int16)
PARTIAL_INTERVAL_SEC = 3.0
MAX_BUFFER_SEC = 12.0

print(f"[stt] loading model={MODEL_NAME} compute={COMPUTE_TYPE}")
model = WhisperModel(MODEL_NAME, compute_type=COMPUTE_TYPE)

def _pcm_to_float(pcm: bytearray):
    return np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0

async def _transcribe(buf: bytearray, beam: int):
    if not buf:
        return ""
    audio = _pcm_to_float(buf)
    segments, _ = model.transcribe(audio, language="en", beam_size=beam, vad_filter=True)
    return "".join(s.text for s in segments).strip()

async def handler(ws):
    buffer = bytearray()
    last_partial = 0.0
    try:
        async for message in ws:
            if isinstance(message, bytes):
                buffer.extend(message)
                now = time.time()
                duration = len(buffer) / (SAMPLE_RATE * SAMPLE_WIDTH)

                # Send partial every PARTIAL_INTERVAL_SEC
                if now - last_partial >= PARTIAL_INTERVAL_SEC:
                    partial = await _transcribe(buffer, beam=2)
                    if partial:
                        await ws.send(json.dumps({"type": "partial", "text": partial}))
                    last_partial = now

                # Finalize when buffer large enough
                if duration >= MAX_BUFFER_SEC:
                    final = await _transcribe(buffer, beam=3)
                    if final:
                        await ws.send(json.dumps({"type": "final", "text": final}))
                    buffer.clear()
                    last_partial = now
            else:
                # Control message (JSON text)
                try:
                    data = json.loads(message)
                except Exception:
                    continue
                cmd = data.get("command")
                if cmd == "flush":
                    final = await _transcribe(buffer, beam=4)
                    if final:
                        await ws.send(json.dumps({"type": "final", "text": final}))
                    buffer.clear(); last_partial = time.time()
                elif cmd == "stop":
                    final = await _transcribe(buffer, beam=4)
                    if final:
                        await ws.send(json.dumps({"type": "final", "text": final}))
                    break
    finally:
        await ws.close()

async def main():
    async with websockets.serve(handler, "0.0.0.0", PORT, max_size=2**23):
        print(f"[stt] ready ws://localhost:{PORT}")
        await asyncio.Future()

if __name__ == "__main__":
    os.environ.setdefault("OMP_NUM_THREADS", "4")
    os.environ.setdefault("NUMBA_NUM_THREADS", "4")
    asyncio.run(main())