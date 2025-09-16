from __future__ import annotations

import time
from pathlib import Path
import streamlit as st

from ai_interviewer.llm import create_llm, ollama_is_running, ollama_list_models
from ai_interviewer.utils.model_catalog import choose_model_for_profile
from ai_interviewer.utils.text import extract_first_question
from ai_interviewer import tts
from ai_interviewer.stt import STTConfig, transcribe_bytes
from ai_interviewer.utils.log import info, warn, error, success, debug


def build_system_prompt(job_role: str) -> str:
    role = job_role.strip() or "General Software Engineer"
    return (
        f"Role: {role}.\n"
        "You are the interviewer. Keep the interview in English only.\n"
        "Ask exactly one question per turn. Be concise (<=25 words). No preface, no quotes, no lists."
    )


def _build_conversation_user_prompt(history: list[dict], latest_user: str | None) -> str:
    parts: list[str] = []
    for m in history:
        r = m.get("role")
        c = (m.get("content") or "").strip()
        if not c:
            continue
        if r == "assistant":
            parts.append(f"Interviewer: {c}")
        else:
            parts.append(f"Candidate: {c}")
    if latest_user:
        parts.append(f"Candidate: {latest_user.strip()}")
    parts.append("Respond as the Interviewer with the next single question only.")
    return "\n".join(parts)


def _mic_widget() -> bytes | None:
    audio_bytes: bytes | None = None
    try:
        from streamlit_mic_recorder import mic_recorder  # type: ignore

        val = mic_recorder(
            start_prompt="🎙️ Record answer",
            stop_prompt="🛑 Stop",
            just_once=True,
            use_container_width=True,
            key="iv_mic",
        )
        if isinstance(val, dict) and "bytes" in val:
            audio_bytes = val["bytes"]
        elif isinstance(val, (bytes, bytearray)):
            audio_bytes = bytes(val)
    except Exception:
        st.info("Microphone widget not available; upload a WAV/MP3/M4A/OGG/FLAC instead.")
        f = st.file_uploader("Upload your answer", type=["wav", "mp3", "m4a", "ogg", "flac"], key="iv_uploader")
        if f:
            audio_bytes = f.read()
    return audio_bytes


def render_interview_tab():
    st.header("AI Interviewer")
    st.caption("Generate an opening question, then record your answer. The interview continues turn-by-turn.")

    job_role = st.text_input("Role", placeholder="e.g., Backend Engineer (Python)")
    speak = st.checkbox("Speak interviewer replies (TTS)", value=False)

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
        user_text = "Start the interview now. Ask the first question only."

        try:
            info("=== LLM CALL (opening) ===")
            info(f"Model: {model} | Host: {st.session_state['ollama_host']}")
            info(system_prompt)
            info(user_text)
        except Exception:
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
            error(f"LLM error: {e}")

        reply = "".join(accum)
        try:
            info("=== RAW LLM OUTPUT ===")
            info(reply)
        except Exception:
            pass

        reply_clean = extract_first_question(reply)
        try:
            success("=== EXTRACTED QUESTION ===")
            success(reply_clean)
        except Exception:
            pass

        if reply_clean:
            st.session_state.setdefault("messages", []).append({"role": "assistant", "content": reply_clean})
            out_container.markdown(f"**Interviewer:** {reply_clean}")
            if speak:
                _speak(reply_clean)

    st.divider()
    st.subheader("Answer")
    st.caption("Record your answer. When you stop, it will be transcribed and sent to the interviewer.")

    audio_bytes = _mic_widget()
    if audio_bytes:
        # Save and play back
        Path(".cache/audio").mkdir(parents=True, exist_ok=True)
        ts = int(time.time())
        ans_path = Path(".cache/audio") / f"answer_{ts}.wav"
        ans_path.write_bytes(audio_bytes)
        with open(ans_path, "rb") as f:
            st.audio(f.read())

        # Transcribe
        try:
            cfg = STTConfig(model=st.session_state.get("stt_model", "tiny.en"))
            transcript = transcribe_bytes(audio_bytes, cfg)
            transcript = (transcript or "").strip()
        except Exception as e:
            transcript = ""
            st.error(f"STT failed: {e}")
            error(f"STT failed: {e}")

        if transcript:
            st.markdown(f"**Candidate (you):** {transcript}")
            st.session_state.setdefault("messages", []).append({"role": "user", "content": transcript})
            _continue_interview(job_role, speak)

    # Show last interviewer turn if any
    if st.session_state.get("messages"):
        last = st.session_state["messages"][-1]
        if last.get("role") == "assistant":
            st.markdown(f"**Interviewer:** {last['content']}")


def _continue_interview(job_role: str, speak: bool) -> None:
    ollama_ok, _ = ollama_is_running(st.session_state["ollama_host"])
    if not ollama_ok:
        st.error("Ollama is not running. Start it in the LLM Setup tab.")
        return

    model = st.session_state.get("model") or choose_model_for_profile(
        st.session_state["pc_profile"],
        ollama_list_models(st.session_state["ollama_host"]),
    )
    llm = create_llm("ollama", model, host=st.session_state["ollama_host"], timeout_s=int(st.session_state["timeout_s"]))

    system_prompt = build_system_prompt(job_role)
    user_text = _build_conversation_user_prompt(st.session_state.get("messages", []), latest_user=None)

    try:
        info("=== LLM CALL (follow-up) ===")
        info(f"Model: {model} | Host: {st.session_state['ollama_host']}")
        info(system_prompt)
        info(user_text)
    except Exception:
        pass

    pb = st.progress(0, text="Generating follow-up...")
    accum = []
    progress_val = 0

    try:
        for chunk in llm.stream_reply(system_prompt, user_text):
            accum.append(chunk)
            progress_val = min(99, progress_val + 1)
            pb.progress(progress_val, text="Generating follow-up...")
            time.sleep(0.01)
        pb.progress(100, text="Done.")
    except Exception as e:
        st.error(f"LLM error: {e}")
        error(f"LLM error: {e}")
        return

    reply = "".join(accum)
    try:
        info("=== RAW LLM OUTPUT (follow-up) ===")
        info(reply)
    except Exception:
        pass

    reply_clean = extract_first_question(reply) or reply.strip()
    if reply_clean:
        st.session_state.setdefault("messages", []).append({"role": "assistant", "content": reply_clean})
        st.markdown(f"**Interviewer:** {reply_clean}")
        if speak:
            _speak(reply_clean)


def _speak(text: str) -> None:
    try:
        Path(".cache/audio").mkdir(parents=True, exist_ok=True)
        out_path = str(Path(".cache/audio").joinpath(f"reply_{int(time.time())}.wav"))
        audio_path = tts.synthesize(text, voice=None, out_path=out_path)
        if audio_path and Path(audio_path).exists():
            with open(audio_path, "rb") as f:
                st.audio(f.read(), format="audio/wav")
    except Exception as e:
        st.warning(f"TTS failed: {e}")
