import requests
import json
import streamlit as st

API_URL = "http://localhost:11434/api/chat"
HEADERS = {"Content-Type": "application/json"}


### without streaming api call; full response at once; can comment if not in use
def get_response_from_api(question):
    data = {
        "model": "phi3_gsm8k:Q4_K_M",
        "messages": [{"role": "user", "content": question}],
        "stream": False,
        "options": {
            "temperature": 1.0,
            "repeat_penalty": 1.0,
            "seed": 3407,
            "top_k": 50,
            "top_p": 1.0,
        },
    }
    response = requests.post(API_URL, json=data, headers=HEADERS)

    if response.status_code == 200:
        return response.json().get("message", {}).get("content", "No content")
    else:
        return f"Error: {response.status_code}"


def stream_response(question, history):
    """
    Function to stream response obtained from model hosted with ollama.
    use command: `ollama serve` after setting up the model.
    """
    data = {
        "model": "anishstha245/phi3_gsm8k",
        # "model": "phi3_gsm8k:Q8_0",
        # "model": "phi3:mini",
        # "model": "tinyllama_gsm8k:latest",
        "messages": history + [{"role": "user", "content": question}],
        "stream": True,
        "options": {
            "temperature": 0.0,
            "repeat_penalty": 1.0,
            "seed": 3407,
            "top_k": 50,
            "top_p": 1.0,
        },
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


### Streamlit UI INITIAL V1, can comment if not used
def math_ui_v1():
    """
    Simple initial v1 UI for testing, with no memory.
    """
    st.title("Math Q&A")
    st.write("Ask a question and get an answer from the AI.")

    # User input
    user_question = st.text_area("Enter your question: ")

    if st.button("Get Answer"):
        if user_question:
            with st.spinner("Getting answer..."):
                answer = get_response_from_api(user_question)
                st.write("**Answer:**", answer)
        else:
            st.write("Please enter a question.")


def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
