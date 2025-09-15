import streamlit as st

from ai_interviewer.backend import (
    make_transcript_stub,
    make_reply_stub,
    make_beep_wav_bytes,
    ping_test,
)


st.set_page_config(page_title="AI Interviewer (MVP)")

st.title("AI Interviewer — MVP")
st.write(
    "This minimal app proves the UI can talk to the backend. Click the button to run a backend test."
)

if st.button("Run backend test"):
    with st.spinner("Running backend stubs..."):
        transcript = make_transcript_stub()
        reply = make_reply_stub(transcript)
        wav_bytes = make_beep_wav_bytes()

    st.success("Backend responded. See results below.")

    st.subheader("Transcript (stub)")
    st.text(transcript)

    st.subheader("Interviewer reply (stub)")
    st.text(reply)

    st.subheader("Audio (stub TTS beep)")
    st.audio(wav_bytes, format="audio/wav")

st.divider()
st.caption(
    "MVP only: no STT/LLM/TTS yet. Next iterations will replace stubs with real components."
)

st.divider()
st.header("System Command Demo (Ping)")
st.write("Run a safe, bounded ping to demonstrate backend command execution and UI output.")

with st.form("ping_form"):
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        host = st.text_input("Host", value="8.8.8.8")
    with col2:
        count = st.number_input("Count", min_value=1, max_value=5, value=1, step=1)
    with col3:
        timeout = st.number_input("Timeout (s)", min_value=1.0, max_value=20.0, value=5.0, step=1.0)
    submitted = st.form_submit_button("Run ping test")

if 'ping_result' not in st.session_state:
    st.session_state['ping_result'] = None

if submitted:
    with st.spinner("Pinging..."):
        result = ping_test(host=host.strip(), count=int(count), timeout_s=float(timeout))
    st.session_state['ping_result'] = result

if st.session_state.get('ping_result'):
    r = st.session_state['ping_result']
    status = "✅ Success" if r.get("ok") == "True" else "⚠️ Failed"
    st.subheader(f"Ping result: {status}")
    st.code(r.get("command") or "", language="bash")
    cols = st.columns(2)
    with cols[0]:
        st.markdown("**Return code:**")
        st.write(r.get("returncode"))
        st.markdown("**Duration (s):**")
        st.write(r.get("duration_s"))
        if r.get("error"):
            st.markdown("**Error:**")
            st.write(r.get("error"))
    with cols[1]:
        st.markdown("**Stdout:**")
        st.text(r.get("stdout") or "")
        st.markdown("**Stderr:**")
        st.text(r.get("stderr") or "")
