from __future__ import annotations

import os
import html
import streamlit as st
import streamlit.components.v1 as components

from ai_interviewer.llm import (
    has_ollama_cli,
    ollama_is_running,
    ollama_list_models,
    ollama_quick_test,
    start_ollama_server,
    pull_ollama_model,
    pull_ollama_model_http,
    install_ollama_user_local,
    delete_ollama_model,
    delete_ollama_model_http,
)
from ai_interviewer.utils.ui import (
    pc_profile_model_candidates,
    choose_model_for_profile,
    append_console,
    parse_percent,
    get_model_size_label,
    open_external_console,
    get_console_log_path,
)
from ai_interviewer.profiles import PCProfile, PROFILE_LABELS, normalize_profile


CARD_CSS = """
<style>
.model-card {
    /* Use theme-aware colors so cards look good in light & dark modes */
    border: 2px solid var(--secondary-background-color, #374151);
  border-radius: 10px;
  padding: 12px 14px;
  margin-bottom: 14px;
        background: var(--background-color, #111827);
        cursor: pointer;
}
.border-green { border-color: #22c55e !important; }  /* green-500 */
.border-yellow { border-color: #f59e0b !important; } /* amber-500 */
.border-red { border-color: #ef4444 !important; }    /* red-500 */
.model-title { font-weight: 600; margin-bottom: 6px; color: var(--text-color, #e5e7eb); }
.badge {
  display: inline-block;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 999px;
    background: var(--secondary-background-color, #374151);
    color: var(--text-color, #e5e7eb);
  margin-left: 8px;
}
.btn-row { margin-top: 10px; }
</style>
"""


def render_setup_tab():
    st.header("LLM Setup")
    st.markdown(CARD_CSS, unsafe_allow_html=True)

    # Console controls and live output
    console_container = st.container()
    with console_container:
        st.subheader("Console")
        cc1, cc2 = st.columns([1, 1])
        with cc1:
            st.checkbox("Show console in browser", key="show_browser_console", value=False)
        with cc2:
            if st.button("Open external console window"):
                log_path = get_console_log_path(st.session_state)
                ok, msg = open_external_console(log_path)
                append_console(msg, st.session_state)
                if ok:
                    st.info(f"{msg} Log: {log_path}")
                else:
                    st.warning(msg)
        console_box = st.empty()

    def refresh_console():
        if not st.session_state.get("show_browser_console", False):
            path = get_console_log_path(st.session_state)
            with console_box:
                st.caption(f"Console is streaming to: {path}")
            return
        logs = "\n".join(st.session_state.get("console", []))
        escaped = html.escape(logs)
        html_block = (
            '<div id="console-box" style="height:220px; overflow-y:auto; padding:8px; border:1px solid #374151; border-radius:6px; background: var(--background-color, #111827); color: var(--text-color, #e5e7eb); white-space: pre-wrap; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, \'Liberation Mono\', \'Courier New\', monospace;">%s</div>'
            '<script>(function(){var el=document.getElementById("console-box"); if(el){ el.scrollTop=el.scrollHeight; }})();</script>'
        ) % (escaped,)
        with console_box:
            components.html(html_block, height=240, scrolling=False)

    # Initial console render
    refresh_console()

    # Profiles
    labels = PROFILE_LABELS
    current_profile = normalize_profile(st.session_state.get("pc_profile", PCProfile.LOW))
    try:
        idx = labels.index(current_profile.value)
    except ValueError:
        idx = 0

    colA, colB = st.columns(2)
    with colA:
        selected_label = st.selectbox(
            "Your PC profile",
            options=labels,
            index=idx,
            help="Auto-selects a suitable model.",
        )
        selected_profile = next(p for p in PCProfile if p.value == selected_label)
        if selected_profile != normalize_profile(st.session_state.get("pc_profile")):
            st.session_state["pc_profile"] = selected_profile
            installed_now = ollama_list_models(st.session_state.get("ollama_host", "http://localhost:11434"))
            st.session_state["model"] = choose_model_for_profile(selected_profile, installed_now)

    with colB:
        default_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        ollama_host = st.text_input("Ollama host", value=st.session_state.get("ollama_host", default_host))
        st.session_state["ollama_host"] = ollama_host

    # Availability and management
    cli_ok = has_ollama_cli("ollama")
    if st.button("Check Ollama availability"):
        append_console(f"GET {st.session_state['ollama_host'].rstrip('/')}/api/tags", st.session_state)
        refresh_console()
    ollama_ok, ollama_msg = ollama_is_running(st.session_state["ollama_host"])
    if ollama_ok:
        st.success("Ollama is running")
        append_console("Ollama check: OK", st.session_state)
        refresh_console()
    else:
        st.warning("Ollama not reachable")
        append_console("Ollama check: " + ollama_msg, st.session_state)
        refresh_console()

    cols = st.columns(3)
    with cols[0]:
        if not cli_ok:
            if st.button("Install Ollama (user)"):
                pb = st.progress(0, text="Installing Ollama...")
                last_pct = 0
                for line in install_ollama_user_local():
                    append_console(str(line), st.session_state)
                    refresh_console()
                    pct = parse_percent(str(line))
                    if pct is None:
                        last_pct = min(99, last_pct + 1)
                        pb.progress(last_pct, text="Installing Ollama...")
                    else:
                        pb.progress(pct, text=f"Installing Ollama... {pct}%")
                pb.progress(100, text="Ollama install complete.")
        else:
            st.info("Ollama CLI detected")

    with cols[1]:
        if st.button("Start Ollama"):
            append_console("Running: ollama serve", st.session_state)
            refresh_console()
            ok, msg, _ = start_ollama_server("ollama")
            append_console(msg, st.session_state)
            refresh_console()
            if ok:
                st.success("Starting Ollama server...")
            else:
                st.error(msg)

    with cols[2]:
        if st.button("Quick test"):
            model = st.session_state.get("model") or "tinyllama:1.1b"
            payload = {"model": model, "prompt": 'Say "ready".', "stream": False}
            endpoint = f"{st.session_state['ollama_host'].rstrip('/')}/api/generate"
            append_console(f"POST {endpoint} {payload}", st.session_state)
            refresh_console()
            ok, resp = ollama_quick_test(model, host=st.session_state["ollama_host"])
            if ok:
                st.success("Model ready")
                append_console("Quick test OK: " + resp[:120], st.session_state)
            else:
                st.error("Model not ready")
                append_console("Quick test failed: " + resp, st.session_state)
            refresh_console()

    st.divider()

    # Models and cards
    installed = ollama_list_models(st.session_state["ollama_host"]) if ollama_ok else []
    if not st.session_state.get("model"):
        st.session_state["model"] = choose_model_for_profile(st.session_state["pc_profile"], installed)

    suggestions = pc_profile_model_candidates(st.session_state["pc_profile"])
    all_models: list[str] = []
    for m in suggestions + installed:
        if m not in all_models:
            all_models.append(m)

    # Render cards in rows
    cols_per_row = 3
    for i, model in enumerate(all_models):
        if i % cols_per_row == 0:
            row_cols = st.columns(cols_per_row)
        col = row_cols[i % cols_per_row]
        with col:
            selected = st.session_state.get("model") == model
            is_installed = model in installed

            border_class = "border-green" if selected else ("border-yellow" if is_installed else "border-red")
            status = "selected" if selected else ("installed" if is_installed else "not installed")
            size_label = get_model_size_label(model)

            st.markdown(
                f"""
                <div class=\"model-card {border_class}\">\n                  <div class=\"model-title\">{model}<span class=\"badge\">{status}</span></div>\n                  <div>Local model managed by Ollama.{(' Size: ' + size_label) if size_label else ''}</div>\n                </div>
                """,
                unsafe_allow_html=True,
            )

            btn_cols = st.columns(3)
            with btn_cols[0]:
                if not selected and st.button("Select", key=f"sel_{model}"):
                    st.session_state["model"] = model
                    st.success(f"Selected {model}")
            with btn_cols[1]:
                if not is_installed and st.button("Download", key=f"dl_{model}"):
                    cmd_log = (
                        f"Running: ollama pull {model}" if cli_ok else
                        f"Running: POST {st.session_state['ollama_host'].rstrip('/')}/api/pull {{'name': '{model}', 'stream': True}}"
                    )
                    append_console(cmd_log, st.session_state)
                    refresh_console()
                    pb = st.progress(0, text=f"Pulling {model}...")
                    last_pct = 0
                    lines = pull_ollama_model(model) if cli_ok else pull_ollama_model_http(model, host=st.session_state["ollama_host"]) 
                    for line in lines:
                        text = str(line)
                        append_console(text, st.session_state)
                        refresh_console()
                        pct = parse_percent(text)
                        if pct is None:
                            last_pct = min(99, last_pct + 1)
                            pb.progress(last_pct, text=f"Pulling {model}...")
                        else:
                            pb.progress(pct, text=f"Pulling {model}... {pct}%")
                    pb.progress(100, text=f"{model} pull complete.")
                    st.rerun()
            with btn_cols[2]:
                if is_installed and st.button("Delete", key=f"rm_{model}"):
                    if st.session_state.get("model") == model:
                        st.session_state["model"] = ""
                    lines = delete_ollama_model(model) if cli_ok else delete_ollama_model_http(model, host=st.session_state["ollama_host"])
                    for line in lines:
                        append_console(str(line), st.session_state)
                        refresh_console()
                    st.rerun()

