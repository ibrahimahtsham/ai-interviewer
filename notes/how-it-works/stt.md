# How STT Works (Short & Easy)

## 1. Front-End Audio
- Microphone audio frames (PCM) → optional Voice Activity Detection (VAD)

## 2. Feature Extraction
- Waveform → mel-spectrogram (time–frequency matrix)
- Windowing, FFT, mel filter bank, log scaling, normalization

## 3. Acoustic + Language Modeling
- Encoder network converts spectrogram into latent sequence
- Decoder (CTC / Transducer / Seq2Seq) proposes token sequences
- Beam search keeps top N hypotheses
- Optional external language model rescoring

## 4. Post-Processing
- Add punctuation & casing
- Normalize numbers ("twenty five" → "25")
- Disambiguate homophones via context

## 5. Streaming vs Batch
- Streaming: emits partial words as confidence grows (may revise)
- Batch: processes entire utterance for higher final accuracy

## 6. Confidence & Stabilization
- Early tokens unstable; stabilize after trailing silence or threshold
- Strategies: time-based freeze, entropy threshold, alignment lock

## 7. Latency Levers
- Frame size (10–30 ms)
- Overlap / stride tuning
- Model size / quantization
- GPU vs CPU execution

## Mini Flow
1. Audio chunk arrives
2. Update rolling spectrogram window
3. Encoder forward pass for new frames
4. Update beam/decoder state
5. Emit partial transcript if stable span advanced
6. Finalize on silence or end-of-stream

---