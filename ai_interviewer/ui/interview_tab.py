from __future__ import annotations

import time
from pathlib import Path
import re
import streamlit as st

from ai_interviewer.llm import create_llm, ollama_is_running, ollama_list_models
from ai_interviewer.utils.model_catalog import choose_model_for_profile
from ai_interviewer.utils.text import extract_first_question
from ai_interviewer import tts
from ai_interviewer.utils.log import info, warn, error, success, debug


def build_system_prompt(job_role: str) -> str:
    role = job_role.strip() or "General Software Engineer"
    return (
        f"Role: {role}.\n"
        "Ask one opening interview question.\n"
        "Only the question; one sentence; <=25 words; end with '?'; no labels/preface/quotes/markdown/lists/explanations."
    )


def render_interview_tab():
    st.header("AI Interviewer")
    st.caption("Pick your model in the LLM Setup tab, then generate an opening question.")

    job_role = st.text_input("Role", placeholder="e.g., Backend Engineer (Python)")
    speak = st.checkbox("Speak it (TTS)", value=False)

    if st.button("Generate opening question"):
        ollama_ok, _ = ollama_is_running(st.session_state["ollama_host"])
        if not ollama_ok:
            st.error("Ollama is not running. Start it in the LLM Setup tab.")
            st.stop()

        model = st.session_state.get("model") or choose_model_for_profile(
            st.session_state["pc_profile"],
            ollama_list_models(st.session_state["ollama_host"]),
        )
        llm = create_llm("ollama", model, host=st.session_state["ollama_host"], timeout_s=int(st.session_state["timeout_s"]))

        system_prompt = build_system_prompt(job_role)
        user_text = ("Only output the one-sentence question, nothing else.")

        # --- Debug logging: exact inputs going to the LLM ---
        try:
            info("=== LLM CALL ===")
            info(f"Model: {model}")
            info(f"Host: {st.session_state['ollama_host']}")
            info("=== SYSTEM PROMPT ===")
            info(system_prompt)
            info("=== USER PROMPT ===")
            info(user_text)
        except Exception:
            # Logging should never break the UI
            pass

        out_container = st.empty()
        pb = st.progress(0, text="Generating...")
        accum = []
        progress_val = 0

        try:
            for chunk in llm.stream_reply(system_prompt, user_text):
                accum.append(chunk)
                progress_val = min(99, progress_val + 1)
                pb.progress(progress_val, text="Generating...")
                time.sleep(0.01)
            pb.progress(100, text="Done.")
        except Exception as e:
            out_container.markdown(f"**Interviewer:** [LLM error: {e}]")
            try:
                error(f"LLM error: {e}")
            except Exception:
                pass

        reply = "".join(accum)

        # --- Debug logging: raw model output ---
        try:
            info("=== RAW LLM OUTPUT ===")
            info(reply)
        except Exception:
            pass

        reply_clean = extract_first_question(reply)
        # --- Debug logging: extracted/cleaned question ---
        try:
            success("=== EXTRACTED QUESTION ===")
            success(reply_clean)
        except Exception:
            pass
        if reply_clean:
            out_container.markdown(f"**Interviewer:** {reply_clean}")
            st.session_state.setdefault("messages", []).append({"role": "assistant", "content": reply_clean})

        if reply_clean and speak:
            try:
                out_path = str(Path(".cache/audio").joinpath("opening.wav"))
                audio_path = tts.synthesize(reply_clean, voice=None, out_path=out_path)
                if audio_path and Path(audio_path).exists():
                    with open(audio_path, "rb") as f:
                        st.audio(f.read(), format="audio/wav")
            except Exception as e:
                st.warning(f"TTS failed: {e}")

    if st.session_state.get("messages"):
        last = st.session_state["messages"][-1]
        st.markdown(f"**Interviewer:** {last['content']}")
