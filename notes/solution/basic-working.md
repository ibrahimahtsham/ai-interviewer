# Accuracy-Focused, Free But More Difficult Setup

**STT**: Whisper Large-v3 locally (faster-whisper / whisper.cpp)  
**TTS**: Piper / Coqui (local)  
**Wiring**: Small Python / Node backend + WebSocket:  
• Browser mic → backend STT (partials) → UI text  
• Reply → local TTS → audio back  
**Why**: Best accuracy with zero cloud cost; private / offline.  
**Trade-off**: Setup effort + CPU/GPU demand.