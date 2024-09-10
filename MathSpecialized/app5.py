import streamlit as st
import requests
import json
from langchain.memory import ConversationBufferMemory

API_URL = "http://localhost:11434/api/chat"
HEADERS = {"Content-Type": "application/json"}

# Initialize session state
if "chapter" not in st.session_state:
    st.session_state.chapter = None
if "step" not in st.session_state:
    st.session_state.step = 0
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "qa_messages" not in st.session_state:
    st.session_state.qa_messages = []

def get_response_from_api(prompt):
    data = {
        "model": "anishstha245/phi3_gsm8k:latest",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {
            "temperature": 0.7,
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

def generate_step_content(chapter, step):
    prompt = f"You are a math tutor. Teach step {step} of chapter '{chapter}' in a clear and concise manner. Don't teach a lot of thing at once. There should be one concept at one step. Include an example if appropriate. Example should be short, simple and relevant to the concept taught in step {step}"
    return get_response_from_api(prompt)

def generate_question(chapter):
    prompt = f"Generate a practice question for the chapter '{chapter}'. The question should be suitable for a student who has just learned this topic. Don't provide the answer along with the question."
    return get_response_from_api(prompt)

def check_answer(question, student_answer):
    prompt = f"The question was: '{question}'\nThe student's answer is: '{student_answer}'\nIs this correct? If not, explain the correct approach step-by-step."
    return get_response_from_api(prompt)

st.title("Math Learning AI Chatbot")

# Create tabs for different features
tab1, tab2 = st.tabs(["Chapter-wise Learning", "General Math Q&A"])

with tab1:
    st.header("Chapter-wise Personalized Learning")

    # Chapter selection
    chapters = ["Algebra", "Geometry", "Trigonometry", "Calculus", "Arithmetic", "Probability and Distribution"]
    selected_chapter = st.selectbox("Select a chapter:", chapters)

    if selected_chapter != st.session_state.chapter:
        st.session_state.chapter = selected_chapter
        st.session_state.step = 0
        st.session_state.messages = []

    if st.session_state.chapter:
        if st.session_state.step == 0:
            st.write(f"Let's start learning {st.session_state.chapter}!")
            st.session_state.step += 1

        # Display current step content
        step_content = generate_step_content(st.session_state.chapter, st.session_state.step)
        st.write(f"Step {st.session_state.step}:")
        st.write(step_content)

        # Ask if the student understood
        understood = st.radio("Did you understand this step?", ("Select an option", "Yes", "No"))
        
        if understood == "Yes":
            st.session_state.step += 1
            st.write(f"Great! Moving to step {st.session_state.step}.")

        elif understood == "No":
            st.write("Let's review this step again with a simpler explanation.")
            simpler_explanation = get_response_from_api(f"Explain step {st.session_state.step} of {st.session_state.chapter} in a simpler way. The student hasn't understood the step you recently taught well. Help them study well in concise manner.")
            st.write(simpler_explanation)

        else:
            st.write("Please select an option to continue.")

        # Generate and display a practice question
        if st.button("Generate Practice Question"):
            question = generate_question(st.session_state.chapter)
            st.session_state.current_question = question
            st.write("Practice Question:")
            st.write(question)

        # Answer submission
        if 'current_question' in st.session_state:
            student_answer = st.text_input("Your answer:")
            if st.button("Submit Answer"):
                feedback = check_answer(st.session_state.current_question, student_answer)
                st.write("Feedback:")
                st.write(feedback)

        # Option to move to the next step
        if st.button("Next Step"):
            st.session_state.step += 1

    # Display chat history
    st.subheader("Chat History")
    for message in st.session_state.messages:
        st.write(f"{message['role']}: {message['content']}")

    # Chat input for chapter-specific questions
    user_input = st.text_input("Ask a question about this chapter:")
    if st.button("Send"):
        st.session_state.messages.append({"role": "user", "content": user_input})
        response = get_response_from_api(f"In the context of {st.session_state.chapter}: {user_input}")
        st.session_state.messages.append({"role": "Math Tutor", "content": response})
        st.rerun()

with tab2:
    st.header("General Math Q&A")
    
    # Display Q&A history
    st.subheader("Q&A History")
    for message in st.session_state.qa_messages:
        st.text(f"{message['role'].capitalize()}: {message['content']}")

    # Input for general math questions
    general_question = st.text_input("Ask any math question:")
    if st.button("Ask"):
        st.session_state.qa_messages.append({"role": "user", "content": general_question})
        response = get_response_from_api(f"Answer this math question: {general_question}")
        st.session_state.qa_messages.append({"role": "assistant", "content": response})
        st.rerun()