from __future__ import annotations

import time
from pathlib import Path
import streamlit as st

from ai_interviewer.llm import create_llm, ollama_is_running, ollama_list_models
from ai_interviewer.utils.ui import choose_model_for_profile
from ai_interviewer import tts


def build_system_prompt(job_role: str) -> str:
    role = job_role.strip() or "General Software Engineer"
    return (
        "You are an AI interviewer. Always respond in English in a professional, concise manner. "
        "You ask one question at a time and adapt follow-ups based on the candidate's answers. "
        f"You are interviewing a candidate for the position of {role}. Start with a single strong opening question."
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
        user_text = "Please start the interview with one opening question."

        out_container = st.empty()
        pb = st.progress(0, text="Generating...")
        accum = []
        progress_val = 0

        try:
            for chunk in llm.stream_reply(system_prompt, user_text):
                accum.append(chunk)
                out_container.markdown(f"**Interviewer:** {''.join(accum)}")
                progress_val = min(99, progress_val + 1)
                pb.progress(progress_val, text="Generating...")
                time.sleep(0.01)
            pb.progress(100, text="Done.")
        except Exception as e:
            out_container.markdown(f"**Interviewer:** [LLM error: {e}]")

        reply = "".join(accum)
        if reply:
            st.session_state["messages"].append({"role": "assistant", "content": reply})

        if reply and speak:
            try:
                out_path = str(Path(".cache/audio").joinpath("opening.wav"))
                audio_path = tts.synthesize(reply, voice=None, out_path=out_path)
                if audio_path and Path(audio_path).exists():
                    with open(audio_path, "rb") as f:
                        st.audio(f.read(), format="audio/wav")
            except Exception as e:
                st.warning(f"TTS failed: {e}")

    if st.session_state.get("messages"):
        last = st.session_state["messages"][-1]
        st.markdown(f"**Interviewer:** {last['content']}")
