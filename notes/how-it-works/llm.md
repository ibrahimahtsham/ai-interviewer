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