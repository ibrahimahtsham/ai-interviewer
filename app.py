import os
import streamlit as st

from ai_interviewer.config import load_config
from ai_interviewer.profiles import normalize_profile
from ai_interviewer.ui.setup_tab import render_setup_tab
from ai_interviewer.ui.interview_tab import render_interview_tab
from ai_interviewer.ui.stt_tab import render_stt_tab
from ai_interviewer.ui.transcript_tab import render_transcript_tab


st.set_page_config(page_title="AI Interviewer", page_icon="🎙️", layout="wide")


def main():
	cfg = load_config()

	# Session defaults
	st.session_state.setdefault("pc_profile", normalize_profile(cfg.pc_profile))
	st.session_state.setdefault("ollama_host", os.getenv("OLLAMA_HOST", "http://localhost:11434"))
	st.session_state.setdefault("timeout_s", int(os.getenv("OLLAMA_TIMEOUT", "600")))
	st.session_state.setdefault("model", cfg.llm_model)
	st.session_state.setdefault("stt_model", os.getenv("STT_MODEL", "tiny.en"))
	st.session_state.setdefault("messages", [])

	tab_interview, tab_llm, tab_stt, tab_transcript = st.tabs(["Interview", "LLM Setup", "STT Setup", "Transcript"])

	with tab_llm:
		render_setup_tab()
	with tab_stt:
		render_stt_tab()
	with tab_interview:
		render_interview_tab()
	with tab_transcript:
		render_transcript_tab()

	st.caption("Tip: Set your PC profile in the LLM/STT Setup tabs; model selections will update automatically.")


if __name__ == "__main__":
	main()

