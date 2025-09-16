from __future__ import annotations

import streamlit as st


def render_transcript_tab():
    st.header("Transcript")
    msgs = st.session_state.get("messages", [])
    if not msgs:
        st.info("No conversation yet.")
        return

    for m in msgs:
        role = m.get("role", "assistant")
        content = m.get("content", "")
        if role == "assistant":
            st.markdown(f"**Interviewer:** {content}")
        else:
            st.markdown(f"**Candidate:** {content}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear transcript"):
            st.session_state["messages"] = []
            st.success("Cleared.")
            st.rerun()
    with col2:
        st.caption(f"Turns: {len(msgs)}")
