import os
import streamlit as st
from pathlib import Path
from langchain.memory import ConversationBufferMemory
from mathutils.personalized_learning import course_dashboard
from mathutils.dynamic_content import create_db
from config.mathutils import stream_response, load_css

# Ensure database and tables are created
create_db()

# Load the custom CSS
css_file_path = Path(__file__).parent / "pages" / "assets" / "css" / "math.css"
load_css(css_file_path)

# Initialize memory for conversation history
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory()
memory = st.session_state.memory

# Set app_mode by default to "Math Specialization Learning"
app_mode = "Math Specialization Learning"

# Load the main app content
course_dashboard()

# Math QA interface at the end of the sidebar
with st.sidebar:
    st.header("Math QA", anchor=False)

    # Sidebar controls for memory options
    no_memory = st.checkbox("No Memory", value=True)
    if no_memory:
        limit_memory = st.checkbox("Limit Memory", value=False, disabled=True)
    else:
        limit_memory = st.checkbox("Limit Memory", value=True)

    if not no_memory and limit_memory:
        memory_limit = st.number_input(
            "Number of conversations to remember:", min_value=1, max_value=10, value=4
        )
    else:
        memory_limit = 4

    if st.button("New Chat"):
        st.session_state.clear()
        st.session_state.memory = ConversationBufferMemory()

    # Initialize session state for messages
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Always show the input field at the bottom
    query = st.chat_input("Ask your math query")  # Input at the bottom

    # Handle user input if available
    if query:
        st.session_state.messages = [{"role": "user", "content": query}]

        # Display the user's query
        with st.chat_message("user"):
            st.code(query)

        # Stream the response from the assistant
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            response_text = ""

            # Do not use memory for previous conversations
            conversation_history = []

            # Stream the response and update the UI
            for ast_mess in stream_response(query, conversation_history):
                response_text = ast_mess
                message_placeholder.code(response_text)

            # Append latest response to the conversation history in session state
            st.session_state.messages.append(
                {"role": "assistant", "content": response_text}
            )
