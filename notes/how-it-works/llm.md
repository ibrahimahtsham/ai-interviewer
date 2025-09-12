# How LLM Works (Short & Easy)

## 1. Input Processing
- **Text input:** User or system provides a prompt or question.
- **Tokenization:** Text is split into tokens (words, subwords, or characters).

## 2. Model Inference
- **Embedding:** Tokens are converted to vectors.
- **Neural network:** Transformer layers process vectors, attending to context and meaning.
- **Decoding:** Predicts next token(s) step-by-step, using context and probabilities.

## 3. Output Generation
- **Sampling:** Chooses next token(s) using temperature, top-k, or nucleus sampling.
- **Detokenization:** Converts tokens back to readable text.
- **Streaming:** Can send partial output as it generates (for chat/voice apps).

## 4. Post-Processing
- **Formatting:** Adds punctuation, fixes casing, applies templates if needed.
- **Filtering:** Removes unsafe or unwanted content.

## 5. Special Features
- **Context window:** Remembers recent tokens (limited by model size).
- **System/user roles:** Can separate instructions from user input.
- **Function calling:** Can trigger code or API calls from text.

---

## Example Flow
1. User: "What is the capital of France?"
2. LLM tokenizes input, processes with transformer, predicts: "The capital of France is Paris."
3. Output is streamed or sent as a complete reply.
