# How TTS Works (Short & Practical)

## 1. Input Text Processing
- Normalize (numbers, dates, abbreviations)
- Tokenize (words / subwords / phonemes)
- Optional: G2P (grapheme-to-phoneme) conversion

## 2. Linguistic / Prosody Features
- Part-of-speech tagging
- Prosody prediction (phrasing, stress, intonation)
- Duration + pitch + energy targets (in modern neural pipelines may be implicit)

## 3. Acoustic Generation
Two main families:
- Parametric (older) / Concatenative (legacy)
- Neural: Tacotron / FastSpeech / VITS / GPT-style audio models

Modern stack example (VITS-like):
1. Text/phonemes → encoder embeddings
2. Variance predictors (duration / pitch / energy)
3. Latent representation sampled
4. Flow / diffusion / autoregressive step refines representation
5. Neural vocoder converts latent → waveform

## 4. Vocoders
- Converts intermediate representation (mel or latent) → PCM audio
- Common types: HiFi-GAN, WaveRNN, WaveGlow, Diffusion, Codec decoders

## 5. Streaming vs Non-Streaming
- Non-stream: generate full mel then vocode → higher latency but simple
- Chunked streaming: generate mel frames progressively
- Low-latency: codec-based discrete tokens (e.g., EnCodec) + AR/parallel decode

## 6. Control Knobs
- Speaking rate
- Pitch shift / style / emotion
- Voice selection / cloning (speaker embedding)

## 7. Latency Factors
- Model size & architecture
- Frame or hop size for streaming
- GPU vs CPU (quantized models help locally)

## 8. Quality Dimensions
- Naturalness (prosody variability)
- Intelligibility (clarity at different speeds)
- Expressiveness (emotion/styling)
- Latency (time to first audio + total synthesis)

## Mini Flow
1. Input text → normalization
2. Convert to phonemes
3. Encode → predict prosody/variance
4. Generate mel/latent sequence
5. Vocoder → audio chunks
6. Stream or play after buffer fill

---
