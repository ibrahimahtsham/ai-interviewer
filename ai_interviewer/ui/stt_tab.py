from __future__ import annotations

import streamlit as st

from ai_interviewer.profiles import PCProfile, PROFILE_LABELS, normalize_profile
from ai_interviewer.stt import stt_model_candidates, choose_stt_model_for_profile, STTConfig, transcribe_bytes
from ai_interviewer.utils.log import info, warn, error, success


def _mic_input_widget() -> bytes | None:
    """Prefer streamlit-mic-recorder; fallback to file upload."""
    audio_bytes: bytes | None = None
    try:
        # streamlit-mic-recorder package
        from streamlit_mic_recorder import mic_recorder  # type: ignore

        val = mic_recorder(
            start_prompt="🎙️ Start recording",
            stop_prompt="🛑 Stop",
            just_once=True,
            use_container_width=True,
            key="stt_setup_mic",
        )
        # It returns dict OR bytes depending on version
        if isinstance(val, dict) and "bytes" in val:
            audio_bytes = val["bytes"]
        elif isinstance(val, (bytes, bytearray)):
            audio_bytes = bytes(val)
    except Exception:
        st.info("Microphone widget not available; upload a WAV/MP3/etc instead.")
        f = st.file_uploader("Upload audio", type=["wav", "mp3", "m4a", "ogg", "flac"])
        if f:
            audio_bytes = f.read()

    return audio_bytes


def render_stt_tab():
    st.header("STT Setup")

    # Profile-driven suggestions
    labels = PROFILE_LABELS
    current_profile = normalize_profile(st.session_state.get("pc_profile", PCProfile.LOW))
    try:
        idx = labels.index(current_profile.value)
    except ValueError:
        idx = 0

    colA, colB = st.columns(2)
    with colA:
        selected_label = st.selectbox("Your PC profile", options=labels, index=idx)
        selected_profile = next(p for p in PCProfile if p.value == selected_label)
        if selected_profile != normalize_profile(st.session_state.get("pc_profile")):
            st.session_state["pc_profile"] = selected_profile
            if not st.session_state.get("stt_model"):
                st.session_state["stt_model"] = choose_stt_model_for_profile(selected_profile)

    with colB:
        st.caption("Whisper model (English only)")
        cands = stt_model_candidates(st.session_state.get("pc_profile", PCProfile.LOW))
        current_stt = st.session_state.get("stt_model") or choose_stt_model_for_profile(st.session_state.get("pc_profile", PCProfile.LOW))
        try:
            index = cands.index(current_stt)
        except Exception:
            index = 0
        sel = st.selectbox("STT Model", options=cands, index=index)
        st.session_state["stt_model"] = sel

    st.divider()
    st.subheader("Quick test")
    st.caption("Record a short sample to verify STT works (requires mic permission).")

    audio_bytes = _mic_input_widget()
    if audio_bytes:
        try:
            cfg = STTConfig(model=st.session_state.get("stt_model", "tiny.en"))
            text = transcribe_bytes(audio_bytes, cfg)
            if text:
                st.success(f"Transcribed: {text}")
                success(f"STT OK: {text}")
            else:
                st.warning("No speech detected.")
        except Exception as e:
            error(f"STT error: {e}")
            st.error(f"STT error: {e}")
