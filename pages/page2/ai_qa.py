import streamlit as st
import json
from config.config import (
    stream_response,
    set_moa_agent,
)
from moa.agent import MOAgent

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

set_moa_agent()

# #Main app layout
# st.header("Mixture of Agents", anchor=False)

# Chat interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if query := st.chat_input("Ask a question"):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.write(query)

    moa_agent: MOAgent = st.session_state.moa_agent
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        ast_mess = stream_response(moa_agent.chat(query, output_format="json"))
        response = st.write_stream(ast_mess)

    st.session_state.messages.append({"role": "assistant", "content": response})

# Option to start a new conversation
with st.form("new_conversation"):
    if st.form_submit_button("Start New Conversation"):
        st.session_state.messages = []
        st.rerun()
