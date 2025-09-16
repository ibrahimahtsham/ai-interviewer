import os
import streamlit as st

from ai_interviewer.config import load_config
from ai_interviewer.profiles import normalize_profile
from ai_interviewer.ui.setup_tab import render_setup_tab
from ai_interviewer.ui.interview_tab import render_interview_tab


st.set_page_config(page_title="AI Interviewer", page_icon="🎙️", layout="wide")


def main():
	cfg = load_config()

	# Session defaults
	st.session_state.setdefault("pc_profile", normalize_profile(cfg.pc_profile))
	st.session_state.setdefault("ollama_host", os.getenv("OLLAMA_HOST", "http://localhost:11434"))
	st.session_state.setdefault("timeout_s", int(os.getenv("OLLAMA_TIMEOUT", "600")))
	st.session_state.setdefault("model", cfg.llm_model)
	st.session_state.setdefault("messages", [])

	tab_interview, tab_llm = st.tabs(["Interview", "LLM Setup"])

	with tab_llm:
		render_setup_tab()
	with tab_interview:
		render_interview_tab()

	st.caption("Tip: Set your PC profile in LLM Setup; the model selection will update automatically.")


if __name__ == "__main__":
	main()

