# How STT Works (My Basic Understanding)

> Audio → mel‑spectrogram (a time‑frequency “picture”). Neural acoustic model reads that picture and predicts sub‑words / words. Decoder finds the best sentence: uses beam search (keep top N options), a language model for fluent grammar, adds punctuation/casing, and fixes homophones by context. Streaming: commits words gradually as confidence rises. Batch: can rescore the whole utterance for max accuracy.

## Simplified Steps
1. Capture audio waveform.
2. Turn audio into a mel‑spectrogram (visual-like matrix of energy over time & frequency).
3. Acoustic model converts spectrogram slices → token probability distributions.
4. Decoder assembles the most likely word sequence:
	- Beam search keeps several competing hypotheses.
	- Language model nudges toward fluent phrasing.
	- Adds casing & punctuation.
	- Context resolves homophones ("there" vs "their").
5. Output mode:
	- Streaming: partial words appear early; may revise.
	- Batch: waits, then produces a cleaner final result (can rescore).

## Key Concepts (One-Liners)
- Mel-spectrogram: compressed, perceptually weighted view of audio.
- Acoustic model: maps sound patterns → linguistic units.
- Beam search: explore multiple candidate transcripts simultaneously.
- Language model assist: improves grammar & coherence.
- Streaming trade-off: lower latency vs early instability.

## Mini Flow (Compact)
Audio → Mel features → Acoustic model scores → Beam + LM → (Add punctuation/case) → Transcript

---