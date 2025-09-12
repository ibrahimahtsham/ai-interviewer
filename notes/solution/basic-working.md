# Accuracy-Focused Local Stack (Free, Higher Setup Effort)

## Stack
- STT: Whisper Large-v3 (faster-whisper / whisper.cpp) locally
- TTS: Piper / Coqui (local)
- Orchestration: Lightweight Python or Node backend + WebSocket
	- Browser mic → backend (streaming STT partials) → UI text
	- LLM reply → local TTS synth → audio stream back to UI

## Why This Setup
- Zero per-minute cloud cost
- Strong accuracy (Whisper large)
- Private / offline capable
- Trade-offs: Initial model downloads, GPU/CPU demand, more glue code

## Data Flow
1. User speaks (browser MediaStream)
2. Audio chunks → backend → streaming STT partial transcripts
3. Partial + final text displayed
4. Text sent to LLM (local or API)
5. LLM response text → local TTS → audio buffer/stream → playback

## Operational Concerns
- Barge-in (interrupt playback when user starts speaking)
- Latency tuning (frame size, VAD, batching)
- Error handling (device permission, dropped websocket)
- Format conversions (PCM ↔ float32, sample rate alignment)

---

# DIY vs Vapi / OpenAI Realtime (In Your Words)

## DIY
"I tell each box how to talk."
- You explicitly connect mic → STT → LLM → TTS → audio
- Must manage:
	- Timing / turn-taking
	- Interruptions (barge-in)
	- Streaming protocols
	- Error recovery
	- Latency optimizations
	- Media formats

## Vapi / Realtime API
"I pick which boxes; it decides the choreography."
- You configure STT + LLM + TTS + policies
- Call start()
- Service handles:
	- Mic ↔ STT ↔ LLM ↔ TTS pipeline
	- Turn-taking / barge-in
	- Event model for UI
	- Session state

## When To Use Which
| Need | DIY Local Stack | Realtime API |
|------|-----------------|--------------|
| Zero usage cost | Yes | No (usually) |
| Fast prototype | Slower | Faster |
| Full control | Maximum | Abstracted |
| Lowest latency (local) | Possible | Depends |
| Compliance / air‑gapped | Yes | Harder |
| Less code to maintain | No | Yes |

---