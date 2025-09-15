import os
from pathlib import Path

import streamlit as st

from ai_interviewer.config import load_config
from ai_interviewer.llm import (
	create_llm,
	ollama_is_running,
	ollama_list_models,
	ollama_quick_test,
	has_ollama_cli,
	start_ollama_server,
	pull_ollama_model,
	pull_ollama_model_http,
		install_ollama_user_local,
)
from ai_interviewer import tts


st.set_page_config(page_title="AI Interviewer (Minimal)", page_icon="🎙️", layout="centered")


def build_system_prompt(job_role: str) -> str:
	role = job_role.strip() or "General Software Engineer"
	return (
		"You are an AI interviewer. Always respond in English in a professional, concise manner. "
		"You ask one question at a time and adapt follow-ups based on the candidate's answers. "
		f"You are interviewing a candidate for the position of {role}. Start with a single strong opening question."
	)


def pc_profile_model_candidates(profile: str):
	"""Return a list of suggested Ollama model names based on PC profile.
	We pick a few widely-available models; availability still depends on what's installed.
	"""
	profile = (profile or "cpu").lower()
	if profile == "gpu":
		return ["llama3", "llama3:8b", "qwen2.5", "mistral", "phi4"]
	if profile in {"low-cpu", "low"}:
		# smaller or lighter variants
		return ["llama3:8b", "phi4", "mistral"]
	# cpu default
	return ["llama3:8b", "mistral", "phi4", "qwen2.5"]


def main():
	cfg = load_config()

	st.title("AI Interviewer (WIP)")
	st.caption("Minimal scaffolding: select your PC profile, choose an LLM, and generate an opening interviewer prompt.")

	with st.sidebar:
		st.header("Setup")
		pc_profile = st.selectbox(
			"Your PC profile",
			options=["low-cpu", "cpu", "gpu"],
			index=["low-cpu", "cpu", "gpu"].index("low-cpu"),
			help="Pick a rough profile to set sensible defaults.",
		)
		backend = "ollama"
		st.text_input("LLM backend", value=backend, disabled=True)
		# Ollama readiness and controls
		if "ollama_cmd" not in st.session_state:
			st.session_state["ollama_cmd"] = "ollama"
		ollama_cmd = st.text_input("Ollama command (path or name)", value=st.session_state["ollama_cmd"], help="If Ollama isn't on PATH, provide full path to the 'ollama' binary." )
		st.session_state["ollama_cmd"] = ollama_cmd

		ollama_host = st.text_input("Ollama host", value=os.getenv("OLLAMA_HOST", "http://localhost:11434"), help="Change if your server runs on another host/port.")
		timeout_s = st.number_input("Request timeout (sec)", min_value=30, max_value=1800, value=int(os.getenv("OLLAMA_TIMEOUT", "600")), help="Increase if your first generation takes longer (model loading).")
		ollama_ok, ollama_msg = ollama_is_running(ollama_host)
		cli_ok = has_ollama_cli(ollama_cmd)

		controls_col1, controls_col2, controls_col3 = st.columns(3)
		with controls_col1:
			if st.button("Start Ollama server"):
				ok, msg, _ = start_ollama_server(ollama_cmd)
				st.toast(msg)
		with controls_col2:
			model_pull = st.text_input("Model to pull", value="llama3:8b")
			if st.button("Pull model"):
				st.session_state.setdefault("logs", [])
				with st.spinner(f"Pulling {model_pull}..."):
					if has_ollama_cli(ollama_cmd):
						for line in pull_ollama_model(model_pull, cmd=ollama_cmd):
							logs = st.session_state.get("logs", [])
							logs.append(line)
							st.session_state["logs"] = logs
							st.write(line)
					else:
						for line in pull_ollama_model_http(model_pull):
							logs = st.session_state.get("logs", [])
							logs.append(line)
							st.session_state["logs"] = logs
							st.write(line)
				st.toast("Pull finished (see Logs)")
		with controls_col3:
			if st.button("Refresh status"):
				st.rerun()

		if not cli_ok:
			st.warning("'ollama' CLI not found. You can install it locally (no sudo) to ~/.local/bin.")
			if st.button("Install Ollama locally"):
				st.session_state.setdefault("logs", [])
				with st.spinner("Installing Ollama..."):
					last_path = None
					for line in install_ollama_user_local():
						logs = st.session_state.get("logs", [])
						logs.append(str(line))
						st.session_state["logs"] = logs
						st.write(str(line))
						if isinstance(line, str) and line.startswith("/") and line.endswith("ollama"):
							last_path = line
					if last_path:
						st.session_state["ollama_cmd"] = last_path
						st.success(f"Ollama installed: {last_path}")
						st.info("Click 'Start Ollama server' then 'Refresh status'.")

		if ollama_ok:
			st.success("Ollama detected")
			if not cli_ok:
				st.info("'ollama' CLI not found or not executable. You can still pull models via HTTP if the server is running.")
			installed = ollama_list_models(ollama_host)
			suggestions = pc_profile_model_candidates(pc_profile)
			model_choices = installed or suggestions
			model = st.selectbox(
				"Model name",
				options=model_choices,
				index=0 if model_choices else 0,
				help="Pick an installed model, or install via 'ollama pull <model>'",
			)
			with st.expander("Verify model readiness", expanded=False):
				if st.button("Run quick test", key="test-model"):
					ok, resp = ollama_quick_test(model, host=ollama_host)
					if ok:
						st.success("Model responded: " + resp[:200])
					else:
						st.error("Test failed: " + resp)
		else:
			st.error("Ollama not detected: " + ollama_msg)
			st.info("Install Ollama: https://ollama.com/download and ensure the 'ollama' binary is in your PATH.")
			st.caption("On Linux you can also enable as a service: sudo systemctl enable --now ollama")
			model = st.text_input("Model name", value="llama3:8b")

	st.subheader("Prep the interview")
	job_role = st.text_input("What role are you interviewing for?", placeholder="e.g., Backend Engineer (Python)")

	if "messages" not in st.session_state:
		st.session_state["messages"] = []

	col1, col2, col3 = st.columns(3)
	with col1:
		generate = st.button("Generate opening question", disabled=(not ollama_ok))
	with col2:
		speak = st.checkbox("Speak the question (TTS)", value=False)
	with col3:
		clear = st.button("Clear logs")

	if clear:
		st.session_state.pop("logs", None)

	# Logging helper
	def log(msg: str):
		logs = st.session_state.setdefault("logs", [])
		logs.append(msg)
		st.session_state["logs"] = logs

	if generate:
		if backend == "ollama":
			if not ollama_ok:
				st.stop()
			st.info("Using Ollama backend.")
		llm = create_llm(backend, model, host=ollama_host, timeout_s=int(timeout_s))
		# Build system prompt from role
		system_prompt = build_system_prompt(job_role)
		user_text = "Please start the interview with one opening question."
		with st.spinner("Asking the interviewer model..."):
			reply = llm.generate_reply(system_prompt, user_text)
		st.session_state["messages"].append({"role": "assistant", "content": reply})
		log("Generated opening question via LLM")
		if "[LLM error:" in reply and "Read timed out" in reply:
			st.info("Tip: Increase the 'Request timeout (sec)' in the sidebar or wait for the model to finish loading, then try again.")

	# Show messages
	for m in st.session_state["messages"]:
		if m["role"] == "assistant":
			st.markdown(f"**Interviewer:** {m['content']}")

	# TTS if requested
	if st.session_state.get("messages") and speak:
		last_msg = st.session_state["messages"][-1]["content"]
		try:
			out_path = str(Path(".cache/audio").joinpath("opening.wav"))
			audio_path = tts.synthesize(last_msg, voice=None, out_path=out_path)
			if audio_path and Path(audio_path).exists():
				with open(audio_path, "rb") as f:
					st.audio(f.read(), format="audio/wav")
				log(f"Audio saved to {audio_path}")
		except Exception as e:
			st.warning(f"TTS failed: {e}")
			log(f"TTS error: {e}")

	# Log display
	st.subheader("Logs")
	for line in st.session_state.get("logs", []):
		st.text(line)

	st.divider()
	st.caption("Next steps: Add STT to capture your voice, and a chat loop to continue the interview.")


if __name__ == "__main__":
	main()

