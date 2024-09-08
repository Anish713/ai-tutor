import streamlit as st
import tempfile
import os
from langchain.memory import (
    ConversationBufferMemory,
)  # Store and load conversation history
from fpdf import FPDF

# Import Rag classes.
from RAG.RAG import rag


if "assistant" not in st.session_state:
    st.session_state["assistant"] = rag()

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Initializing memory for conversation history
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory()

memory = st.session_state.memory

# Flag for disabling memory
no_memory = st.sidebar.checkbox("No Memory", value=False)

# Disable memory limit if "No Memory" is set True
if no_memory:
    limit_memory = st.sidebar.checkbox("Limit Memory", value=False, disabled=True)
else:
    limit_memory = st.sidebar.checkbox("Limit Memory", value=True)

if not no_memory and limit_memory:
    memory_limit = st.sidebar.number_input(
        "Number of conversations to remember:", min_value=1, max_value=10, value=4
    )
else:
    memory_limit = 0

# New Chat button to clear chat history and memory
if st.sidebar.button("New Chat"):
    st.session_state["messages"] = []
    st.session_state.memory = ConversationBufferMemory()


# Display all messages stored in session_state
def display_messages():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def process_local_file(local_file_path):
    st.session_state["assistant"].clear()
    # st.session_state.messages = []

    if os.path.exists(local_file_path):
        st.session_state["assistant"].feed(local_file_path)
    else:
        st.error("File not found. Please check the file path.")


def process_file():
    st.session_state["assistant"].clear()
    # st.session_state.messages = []

    for file in st.session_state["file_uploader"]:
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            tf.write(file.getbuffer())
            file_path = tf.name

        with st.session_state["feeder_spinner"], st.spinner("Uploading the file"):
            st.session_state["assistant"].feed(file_path)
        os.remove(file_path)


def process_input():

    if "memory" not in st.session_state:
        st.session_state.memory = ConversationBufferMemory()
    memory = st.session_state.memory

    # See if user has typed in any message and assign to prompt.
    if prompt := st.chat_input("What can i do?"):
        with st.chat_message("user"):
            st.markdown(prompt)

        st.session_state.messages.append({"role": "user", "content": prompt})

        # Generate responnse based on the selected memory option
        if not no_memory:
            conversation_history_str = memory.load_memory_variables({})["history"]
        else:
            conversation_history_str = ""

        conversation_history = []
        if conversation_history_str:
            for line in conversation_history_str.split("\n"):
                if line.startswith("Human:"):
                    conversation_history.append(
                        {"role": "user", "content": line.replace("Human: ", "")}
                    )
                elif line.startswith("AI:"):
                    conversation_history.append(
                        {"role": "assistant", "content": line.replace("AI: ", "")}
                    )

        # Limit the conversation history based on the memory limit
        if limit_memory and len(conversation_history) > memory_limit * 2:
            conversation_history = conversation_history[-memory_limit * 2 :]

        # Generate response and write back to the chat container.
        response = st.session_state["assistant"].ask(
            prompt, context=conversation_history
        )

        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Append the latest response to the conversation history
        conversation_history.append({"role": "user", "content": prompt})
        conversation_history.append({"role": "assistant", "content": response})

        # Update memory if memory is enabled
        if not no_memory:
            st.session_state.memory = ConversationBufferMemory()  # Clear the memory
            memory = st.session_state.memory

            # Save the conversation history to memory
            for i in range(0, len(conversation_history), 2):
                user_input = conversation_history[i]["content"]
                assistant_output = conversation_history[i + 1]["content"]
                memory.save_context({"input": user_input}, {"output": assistant_output})


def generate_pdf(conversation_history):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    for message in conversation_history:
        role = message["role"].capitalize()
        content = message["content"]
        pdf.cell(200, 10, txt=f"{role}: {content}", ln=True)

    pdf_output_path = "conversation_history.pdf"
    pdf.output(pdf_output_path)
    return pdf_output_path


def main():
    st.title("Q&A Chatbot")

    # Initialize the session_state.
    if len(st.session_state) == 0:
        # st.session_state["assistant"] = rag()
        st.session_state.messages = []
        # st.session_state.memory = ConversationBufferMemory()

    local_file_path = "D:\\FuseMachine\\DataSet_RAG\\what-is-ai-v2.pdf"
    # local_file_path = "C:\\Users\\Anish\\Desktop\\projects\\AI_Tutor(exp)\\pages\\page4\\what-is-ai-v2.pdf"
    process_local_file(local_file_path)

    # Code for file upload functionality.
    with st.sidebar:
        st.header("Upload the data of relevent field")
        st.file_uploader(
            "Upload Some Relevent File If You Want",
            type=["pdf"],
            key="file_uploader",
            on_change=process_file,
            label_visibility="collapsed",
            accept_multiple_files=True,
        )

        if st.session_state.messages:
            last_question = next(
                (
                    msg["content"]
                    for msg in reversed(st.session_state.messages)
                    if msg["role"] == "user"
                ),
                None,
            )
            if last_question:
                st.subheader("last Question")
                st.markdown(f"💡 **{last_question}**")

        if st.button("Download Chat as PDF"):
            pdf_path = generate_pdf(st.session_state.messages)
            with open(pdf_path, "rb") as pdf_file:
                st.download_button(
                    label="Download PDF",
                    data=pdf_file,
                    file_name="conversation_history.pdf",
                    mime="application/pdf",
                )

    st.session_state["feeder_spinner"] = st.empty()

    display_messages()
    process_input()


if __name__ == "__main__":
    main()
