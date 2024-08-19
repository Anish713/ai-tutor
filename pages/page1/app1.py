import os
import streamlit as st
from langchain.memory import ConversationBufferMemory
from config.mathutils import *



# math_ui_v1() ###with no memory

### Streamlit UI FINAL
### Initialize memory for conversation history
if "memory" not in st.session_state:  # preserves chat history
    st.session_state.memory = ConversationBufferMemory()
memory = st.session_state.memory

### Add flag "no_memory" for chat with 0 memory
no_memory = st.sidebar.checkbox("No Memory", value=False)

### Disable "Limit Memory" if "No Memory" is set to True
if no_memory:
    limit_memory = st.sidebar.checkbox("Limit Memory", value=False, disabled=True)
else:
    limit_memory = st.sidebar.checkbox("Limit Memory", value=True)

if st.sidebar.button("New Chat"):
    st.session_state.clear()
    st.session_state.memory = ConversationBufferMemory()

### Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

st.header("Math QA", anchor=False)

### Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.code(message["content"])

### Handle user input
if query := st.chat_input("Ask your math query"):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.code(query)
        ############### #TODO: MARKDOWN RESPONSE IS NOT SUITABLE WHEN RENDERING as mathematical problems might contain symbols. .code might be suitable for user query for now.

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        response_text = ""

        ### Get the conversation history from LangChain memory only if no_memory is False
        if not no_memory:
            conversation_history_str = memory.load_memory_variables({})["history"]
        else:
            conversation_history_str = ""

        ### Convert the conversation history string to a list of dictionaries
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

        ### checking conversation history before memory update to see if previous chats are present
        previous_history = memory.load_memory_variables({})["history"]
        # print("Before updating memory, Conversation History:")
        # print(previous_history)
        previous_conversations = len(conversation_history) // 2
        print(f"Number of conversations (previous): {previous_conversations}")
        print("--" * 25)

        ### Stream the response and update the UI
        for ast_mess in stream_response(query, conversation_history):
            response_text = ast_mess
            message_placeholder.code(response_text)
            ############### #TODO: MARKDOWN RESPONSE IS NOT SUITABLE WHEN RENDERING as mathematical problems might contain symbols like $,_, etc which is interpreted different by markdown and latex.

        ### Append latest response to the conversation history
        conversation_history.append({"role": "user", "content": query})
        conversation_history.append({"role": "assistant", "content": response_text})

        ### Limit the history if the flag is set
        if not no_memory and limit_memory and len(conversation_history) > 4:
            conversation_history = conversation_history[-4:]

        ### Clear the memory and save the conversation if no_memory is False
        if not no_memory:
            st.session_state.memory = ConversationBufferMemory()  # Clear the memory
            memory = st.session_state.memory

            for i in range(0, len(conversation_history), 2):
                user_input = conversation_history[i]["content"]
                assistant_output = conversation_history[i + 1]["content"]
                memory.save_context({"input": user_input}, {"output": assistant_output})

            ### checking if history is maintained for confirmation, after update
            current_history = memory.load_memory_variables({})["history"]
            current_conversations = len(conversation_history) // 2
            # print("Current Conversation History:")
            # print(current_history)
            print(f"Number of conversations (current): {current_conversations}")
            print("--" * 25)

    st.session_state.messages.append({"role": "assistant", "content": response_text})
