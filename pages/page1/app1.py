import streamlit as st
import json
import requests
from langchain.memory import ConversationBufferMemory

API_URL = "http://localhost:11434/api/chat"
HEADERS = {"Content-Type": "application/json"}

### Initialize memory for conversation history
if "memory" not in st.session_state:  # preserves chat history
    st.session_state.memory = ConversationBufferMemory()
memory = st.session_state.memory

### Flag to control token limiting
limit_tokens = st.sidebar.checkbox("Limit Tokens", value=False)

if st.sidebar.button("New Chat"):
    st.session_state.clear()
    st.session_state.memory = ConversationBufferMemory()


# ##without streaming api call #full response at once
# def get_response_from_api(question):
#     data = {
#         "model": "phi3:mini",
#         "messages": [{"role": "user", "content": question}],
#         "stream": False
#     }
#     response = requests.post(API_URL, json=data, headers=HEADERS)

#     if response.status_code == 200:
#         return response.json().get('message', {}).get('content', 'No content')
#     else:
#         return f"Error: {response.status_code}"


### Function to stream response from the API
def stream_response(question, history):
    data = {
        "model": "phi3:mini",
        "messages": history + [{"role": "user", "content": question}],
        "stream": True,
    }
    response = requests.post(API_URL, json=data, headers=HEADERS, stream=True)

    if response.status_code == 200:
        response_text = ""
        for line in response.iter_lines():
            if line:
                json_line = json.loads(line.decode("utf-8"))
                content = json_line.get("message", {}).get("content", "")
                response_text += content
                yield response_text
    else:
        yield f"Error: {response.status_code}"


### Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

st.header("Math QA", anchor=False)

### Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

### Handle user input
if query := st.chat_input("Ask your math query"):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.write(query)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        response_text = ""

        ### Get the conversation history from LangChain memory
        conversation_history_str = memory.load_memory_variables({})["history"]

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
        previous_conversations = (
            len(conversation_history) // 2
        )  ## 2 exchanges in 1 conversation
        print(f"Number of conversations (previous): {previous_conversations}")
        print("--" * 25)

        ### Stream the response and update the UI
        for ast_mess in stream_response(query, conversation_history):
            response_text = ast_mess
            message_placeholder.markdown(response_text)

        ### Append latest response to the conversation history
        conversation_history.append({"role": "user", "content": query})
        conversation_history.append({"role": "assistant", "content": response_text})

        ### Limit the history if the flag is set
        if limit_tokens and len(conversation_history) > 20:
            conversation_history = conversation_history[-20:]

        ### Clear the memory and save the conversation
        st.session_state.memory = ConversationBufferMemory()  # Clear the memory
        memory = st.session_state.memory

        for i in range(0, len(conversation_history), 2):
            user_input = conversation_history[i]["content"]
            assistant_output = conversation_history[i + 1]["content"]
            memory.save_context({"input": user_input}, {"output": assistant_output})

        ### ### checking if history is maintained for confirmation, after update
        current_history = memory.load_memory_variables({})["history"]
        current_conversations = len(conversation_history) // 2
        # print("Current Conversation History:")
        # print(current_history)
        print(f"Number of conversations (current): {current_conversations}")
        print("--" * 25)

    st.session_state.messages.append({"role": "assistant", "content": response_text})
