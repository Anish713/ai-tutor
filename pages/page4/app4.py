import streamlit as st
import tempfile
import os

# Import Rag classes.
from .RAG.RAG import rag


if "assistant" not in st.session_state:
    st.session_state["assistant"] = rag()
    
if "messages" not in st.session_state:
    st.session_state["messages"] = []

#Display all messages stored in session_state
def display_messages():
  for message in st.session_state.messages:
    with st.chat_message(message['role']):
      st.markdown(message['content'])

def process_local_file(local_file_path):
  st.session_state["assistant"].clear()
  #st.session_state.messages = []

  if os.path.exists(local_file_path):
    st.session_state["assistant"].feed(local_file_path)
  else:
    st.error("File not found. Please check the file path.")


def process_file():
  st.session_state["assistant"].clear()
  #st.session_state.messages = []

  for file in st.session_state["file_uploader"]:
    with tempfile.NamedTemporaryFile(delete=False) as tf:
      tf.write(file.getbuffer())
      file_path = tf.name

    
    with st.session_state["feeder_spinner"], st.spinner("Uploading the file"):
      st.session_state["assistant"].feed(file_path)
    os.remove(file_path)

def process_input():
  # See if user has typed in any message and assign to prompt.
  if prompt := st.chat_input("What can i do?"):
    with st.chat_message("user"):
      st.markdown(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate response and write back to the chat container.
    response = st.session_state["assistant"].ask(prompt)
    with st.chat_message("assistant"):
      st.code(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

def main():
  st.title("Q&A Chatbot")

  # Initialize the session_state.
  if len(st.session_state) == 0:

    #st.session_state["assistant"] = rag()
    st.session_state.messages = []
  
  #local_file_path = "D:\\FuseMachine\\DataSet_RAG\\what-is-ai-v2.pdf"
  local_file_path = "./RAG/what-is-ai-v2.pdf"
  

  process_local_file(local_file_path)

  # Code for file upload functionality.
  with st.sidebar:
    st.header("Upload the data of relevent field")
    st.file_uploader(
        "Upload Some Relevent File If You Want",
        type = ["pdf"],
        key = "file_uploader",
        on_change=process_file,
        label_visibility="collapsed",
        accept_multiple_files=True,
      )
    
    if st.session_state.messages:
      last_question = next((msg['content'] for msg in reversed(st.session_state.messages) if msg['role'] == 'user'), None)
      if last_question:
        st.subheader("last Question")
        st.markdown(f"💡 **{last_question}**")



  st.session_state["feeder_spinner"] = st.empty()

  display_messages()

  process_input()

if __name__ == "__main__":
  main()
