# How The Interview AI Works (Simple Version)

Think of the system as a small team passing notes:

1. You speak.
2. Speech-To-Text (STT) turns your voice into plain text.
3. A Prompt Builder packs a short snapshot:
   - What the interview is about
   - What was just answered
   - Which topics are left
   - Clear instruction: “Give ONE next question.”
4. The LLM (a text autocomplete brain) reads that snapshot and writes the next question.
5. Text-To-Speech (TTS) reads the question out loud.
6. The loop repeats.

Key Ideas:
- The LLM does NOT remember anything by itself. We must remind it every turn with a small summary.
- If we give it messy or huge text, it gets slower or confused.
- We force structure: “Only one concise question.”
- Smaller model is fine if the instructions are clear.

Very Simple Picture:
Your voice -> STT -> (summary + last answer + instructions) -> LLM -> next question -> TTS -> you answer again.

Why Not Just Let It Talk Freely?
- It might ramble, answer its own questions, or go off-topic.
- Structure keeps it focused and fair.

Core Parts:
- STT: turns sound into text.
- State: tiny record (topics covered, last answer).
- Prompt Builder: assembles the short instruction message.
- LLM: generates the next question.
- TTS: speaks it.
- Controller: glues it all together.

Tiny Pseudocode:
```python
def turn(audio):
    answer = stt(audio)
    prompt = build_prompt(state, answer)
    next_q = llm(prompt)
    speak(next_q)
    update_state(state, answer, next_q)
```

What Makes It “Smart”?
Mostly: good instructions + feeding only what it needs (not everything).

What To Add Later (when ready):
- Topic coverage tracking
- Difficulty adjustment
- Scoring / feedback
- Small document lookup (job description)

Start Small:
1. Hardcode 3–5 seed questions.
2. After each answer ask the model: “Propose the next single follow-up.”
3. Log everything.

That’s the basic

## More Notes: Using LLMs (Beginner-Friendly)

Think of a Large Language Model (LLM) like a super advanced autocomplete. You give it a short setup (prompt), it guesses the next words.

### 1. Two Ways To Use Models
- Hosted (online API): You send text over the internet, it sends back the answer.
- Local (on your laptop): You download the model file (like a giant brain snapshot) and run it yourself.

### 2. Pricing (Hosted APIs)
You usually pay for “tokens.” 1 token ≈ ¾ of a word.

Simple formula: cost ≈ (input_tokens * in_price + output_tokens * out_price) / 1000.

Very rough idea (can change):
- Small cheaper models: less than a cent for a short turn.
- Bigger fancy models: a few cents per turn.

Why it matters: If your prompt is short and answers are short, cost stays tiny.

### 3. Local vs Hosted (Quick Feel)
| Thing | Local | Hosted |
|-------|-------|--------|
| Money per turn | Basically free | You pay each call |
| Setup | You install stuff | Just an API key |
| Speed first token | After load, can be quick | Depends on network |
| Quality ceiling | Limited by your hardware | You can rent huge brains |
| Privacy | Stays with you | You send data out |

For you now: start local for cheap experiments; maybe add hosted fallback later for harder logic.

### 4. Your Laptop Specs (Summary)
- CPU only (older i7, 2 cores / 4 threads effectively)
- 8 GB RAM (not a lot)
- No real GPU for AI

This means: use small models (3B–4B parameters) in “quantized” form (compressed). A 7B model might work but will be slow and eat memory.

### 5. What Is Quantization?
Shrinking the model weights from full precision to fewer bits (like 16 → 4) so it fits in RAM. Slight quality drop, big memory win.

### 6. Model Size vs Approx Memory (4–bit quant)
- 2–3B: ~1.5–2 GB
- 4B: ~2–2.5 GB
- 7B: ~4–5 GB (tight + slow)
- 13B: not realistic here

### 7. Good Starter Models For You
- Phi-3 Mini (≈3.8B) – small, smart for its size.
- Qwen 1.5 4B Instruct – also good.
- (Optional) Mistral 7B Instruct – only if you accept slower speed.

### 8. How To Run Locally (Easiest Path: Ollama)
Ollama = a helper tool that downloads + runs models for you and gives you an HTTP endpoint.

Steps:
1. Install Ollama (one-line script from their site).
2. Pull a model: `ollama pull phi3:mini`
3. Chat: `ollama run phi3:mini`
4. Program use: send POST to `http://localhost:11434/api/generate` with JSON containing model + prompt.

You only need internet for the first download.

### 9. How Hosted API Use Works (Simple)
1. Get API key (like a password). Store safely.
2. Send HTTP request: model name + your prompt + settings (temperature, max tokens).
3. Get back JSON with generated text.

If you later add a hosted fallback, you can route “hard” turns there.

### 10. Integration Pattern (Keep It Swappable)
Wrap both local and hosted in the same interface so you can change later without touching the rest of the code.

Pseudo-interface:
```python
class LLMProvider:
    def generate(self, prompt: str, max_tokens=64, temperature=0.5):
        raise NotImplementedError

class LocalOllama(LLMProvider):
    def generate(...):
        # POST to localhost Ollama server

class HostedAPI(LLMProvider):
    def generate(...):
        # Call remote service (OpenAI / etc.)
```

Then your interviewer logic just calls `provider.generate()`.

### 11. Picking When To Use Which
Simple rule (example):
1. Try local model first.
2. If it takes too long or output is empty / nonsense → retry with hosted model.

### 12. Tuning For One-Question Output
- Keep prompt short: summary + last answer + instruction (“Give ONE next question only”).
- Limit max output tokens (like 48–64).
- Stop when a question mark is produced (optional optimization).

### 13. Avoiding Cost Explosions (Hosted)
- Don’t send full conversation; keep a rolling compact summary.
- Trim user answers if very long (store raw separately if needed).
- Log total tokens per turn so you notice drift.

### 14. When To Upgrade Hardware
- If you want faster responses (<1s) or bigger models (7B+ comfortably) → aim for 32 GB RAM + a GPU with 8–12 GB VRAM.

### 15. Quick Mental Checklist For Each Turn
1. Got audio → text? (STT ok)
2. Summarize state (topics covered, last answer gist)
3. Build prompt (short!)
4. Call LLM (local first)
5. Speak result (TTS)
6. Update state + logs

### 16. Starter Settings Suggestion
- Model: Phi-3 Mini (local)
- Temperature: 0.4–0.5 (keeps it focused)
- Max tokens: 56
- Seed questions: 3–5
- Log: timestamp, provider used, latency ms, tokens used, question text

### 17. Quick Example Local Call (Conceptual)
Request you send to your local server:
```json
{
  "model": "phi3:mini",
  "prompt": "SUMMARY: topics=databases covered: indexing | LAST ANSWER: 'I used Postgres...'\nINSTRUCTION: Ask ONE next interview question about scaling." ,
  "options": {"temperature": 0.5, "num_predict": 56}
}
```

### 18. Small Glossary
- Token: chunk of text (not always a full word)
- Prompt: what you feed the model
- Latency: how long you wait
- Inference: the act of generating text
- Quantized: compressed model version

### 19. Your Minimal Action Plan
1. Install Ollama.
2. Pull phi3:mini.
3. Build tiny Python script with Local provider.
4. Hardcode 3 seed questions.
5. Log outputs.
6. Later add hosted fallback (optional).

Done. Keep it scrappy and small first.
