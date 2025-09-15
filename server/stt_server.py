#!/usr/bin/env python3
import asyncio, json, time, os, traceback
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
PARTIAL_WINDOW_SEC = float(os.getenv("PARTIAL_WINDOW_SEC", "6.0"))
OVERLAP_SEC = float(os.getenv("OVERLAP_SEC", "0.2"))

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
#!/usr/bin/env python3
import asyncio, json, time, os, traceback
import numpy as np
import websockets
from faster_whisper import WhisperModel

MODEL_NAME = os.getenv("WHISPER_MODEL", "tiny.en")
COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE", "int8")
PORT = int(os.getenv("STT_PORT", "8765"))

SAMPLE_RATE = 16000
SAMPLE_WIDTH = 2  # bytes per sample (int16)
PARTIAL_INTERVAL_SEC = 3.0
MAX_BUFFER_SEC = 12.0
PARTIAL_WINDOW_SEC = float(os.getenv("PARTIAL_WINDOW_SEC", "6.0"))

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

def _last_sentence(text: str) -> str:
    if not text:
        return text
    import re
    parts = re.split(r'([\.\?\!\u2026])', text)
    if len(parts) >= 2:
        core = ''.join(parts[-2:]).strip()
        return core if core else text[-120:]
    return text[-120:]

_CONN_SEQ = 0

async def _send_log(ws, text: str, level: str = "info", seq: int | None = None):
    try:
        payload = {"type": "log", "text": text, "level": level, "ts": time.time()}
        if seq is not None:
            payload["seq"] = seq
        await ws.send(json.dumps(payload))
    except Exception:
        pass

async def handler(ws):
    global _CONN_SEQ
    _CONN_SEQ += 1
    conn_id = _CONN_SEQ
    buffer = bytearray()
    last_partial = 0.0
    seq = 0
    await _send_log(ws, f"client connected (conn={conn_id})", seq=seq)
    await _send_log(ws, f"server cfg: SAMPLE_RATE={SAMPLE_RATE}Hz width={SAMPLE_WIDTH}B partial={PARTIAL_INTERVAL_SEC}s maxbuf={MAX_BUFFER_SEC}s", seq=seq)
    frames_rx = 0
    bytes_rx = 0
    last_rx_log = 0.0
    client_rate = None
    processed_bytes = 0
    last_partial_text_sent = ""
    start_time = time.time()
    try:
        async for message in ws:
            if isinstance(message, bytes):
                frames_rx += 1
                bytes_rx += len(message)
                buffer.extend(message)
                now = time.time()
                duration = len(buffer) / (SAMPLE_RATE * SAMPLE_WIDTH)
                uncommitted = max(0, len(buffer) - processed_bytes)
                duration_uncommit = uncommitted / (SAMPLE_RATE * SAMPLE_WIDTH)

                if now - last_rx_log >= 2.0:
                    await _send_log(ws, f"rx: frames={frames_rx} bytes={bytes_rx} buffer_bytes={len(buffer)} approx_dur@{SAMPLE_RATE}Hz={duration:.2f}s uncommitted={duration_uncommit:.2f}s", seq=seq)
                    last_rx_log = now
                    if client_rate and client_rate != SAMPLE_RATE:
                        await _send_log(ws, f"warning: client ctxRate={client_rate}Hz != server SAMPLE_RATE={SAMPLE_RATE}Hz (likely cause of repetitions).", level="warn", seq=seq)

                if now - last_partial >= PARTIAL_INTERVAL_SEC:
                    t0 = time.time()
                    tail_bytes = int(SAMPLE_RATE * SAMPLE_WIDTH * PARTIAL_WINDOW_SEC)
                    start = max(processed_bytes, len(buffer) - tail_bytes)
                    view = buffer[start:] if start < len(buffer) else bytearray()
                    partial_full = await _transcribe(view, beam=2)
                    partial = _last_sentence(partial_full)
                    dt = (time.time() - t0) * 1000
                    if partial and partial != last_partial_text_sent:
                        last_partial_text_sent = partial
                        seq += 1
                        await ws.send(json.dumps({"type": "partial", "text": partial, "seq": seq}))
                        await _send_log(ws, f"partial seq={seq} chars={len(partial)} {dt:.0f}ms buffer={duration:.1f}s uncommit={duration_uncommit:.1f}s window={PARTIAL_WINDOW_SEC:.1f}s", seq=seq)
                        await _send_log(ws, f"partial text: {partial[:120]}{'…' if len(partial)>120 else ''}", seq=seq)
                    last_partial = now

                if duration_uncommit >= MAX_BUFFER_SEC:
                    t0 = time.time()
                    region = buffer[processed_bytes:]
                    final = await _transcribe(region, beam=3)
                    dt = (time.time() - t0) * 1000
                    if final:
                        seq += 1
                        await ws.send(json.dumps({"type": "final", "text": final, "seq": seq}))
                        await _send_log(ws, f"final seq={seq} chars={len(final)} {dt:.0f}ms (buffer reset)", seq=seq)
                        await _send_log(ws, f"final text: {final[:160]}{'…' if len(final)>160 else ''}", seq=seq)
                    processed_bytes = len(buffer)
                    buffer.clear()
                    last_partial = now
                    last_partial_text_sent = ""
            else:
                try:
                    data = json.loads(message)
                except Exception:
                    continue
                if data.get("type") == "meta":
                    meta = data.get("data", {})
                    stats = data.get("stats", {})
                    if isinstance(meta, dict) and "ctxRate" in meta:
                        try:
                            client_rate = int(meta.get("ctxRate"))
                        except Exception:
                            pass
                    await _send_log(ws, f"meta: {meta} stats: frames={stats.get('frames')} bytes={stats.get('bytes')} uptimeMs={stats.get('uptimeMs')}", seq=seq)
                    continue
                cmd = data.get("command")
                if cmd == "flush":
                    await _send_log(ws, "flush command received", seq=seq)
                    t0 = time.time()
                    region = buffer[processed_bytes:]
                    final = await _transcribe(region, beam=4)
                    dt = (time.time() - t0) * 1000
                    if final:
                        seq += 1
                        await ws.send(json.dumps({"type": "final", "text": final, "seq": seq}))
                        await _send_log(ws, f"flush final seq={seq} chars={len(final)} {dt:.0f}ms", seq=seq)
                        await _send_log(ws, f"final text: {final[:160]}{'…' if len(final)>160 else ''}", seq=seq)
                    processed_bytes = len(buffer)
                    buffer.clear(); last_partial = time.time(); last_partial_text_sent = ""
                elif cmd == "stop":
                    await _send_log(ws, "stop command received", seq=seq)
                    t0 = time.time()
                    region = buffer[processed_bytes:]
                    final = await _transcribe(region, beam=4)
                    dt = (time.time() - t0) * 1000
                    if final:
                        seq += 1
                        await ws.send(json.dumps({"type": "final", "text": final, "seq": seq}))
                        await _send_log(ws, f"stop final seq={seq} chars={len(final)} {dt:.0f}ms", seq=seq)
                        await _send_log(ws, f"final text: {final[:160]}{'…' if len(final)>160 else ''}", seq=seq)
                    processed_bytes = len(buffer)
                    break
    except Exception as e:
        tb = traceback.format_exc(limit=4)
        await _send_log(ws, f"exception: {e.__class__.__name__}: {e}", level="error", seq=seq)
        await _send_log(ws, tb, level="error", seq=seq)
        try:
            await ws.send(json.dumps({"type": "error", "error": str(e), "kind": e.__class__.__name__}))
        except Exception:
            pass
    finally:
        uptime = time.time() - start_time
        await _send_log(ws, f"client disconnected conn={conn_id} uptime={uptime:.1f}s", seq=seq)
        try:
            await ws.close()
        except Exception:
            pass

async def main():
    async with websockets.serve(handler, "0.0.0.0", PORT, max_size=2**23):
        print(f"[stt] ready ws://localhost:{PORT}")
        await asyncio.Future()

if __name__ == "__main__":
    os.environ.setdefault("OMP_NUM_THREADS", "4")
    os.environ.setdefault("NUMBA_NUM_THREADS", "4")
    asyncio.run(main())