import streamlit as st
import tempfile
import os
from langchain.memory import ConversationBufferMemory
from fpdf import FPDF
from RAG.RAG import rag
import hashlib
from pathlib import Path
import json
import csv 
import datetime
from config.mathutils import stream_response, load_css


st.session_state.step = 0

def save_response(level, question, response):
    file_name = f"{level}_responses.csv"
    time_stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(file_name, 'a', newline = '', encoding = 'utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([time_stamp, question, response])


# Initialize session state
def initialize_session_state():
    if "assistants" not in st.session_state:
        st.session_state["assistants"] = {
            "basic": rag("./chroma_db_basic"),
            "intermediate": rag("./chroma_db_intermediate"),
            "advanced": rag("./chroma_db_advanced")
        }
    if "messages" not in st.session_state:
        st.session_state["messages"] = {"basic": [], "intermediate": [], "advanced": []}
    if "memory" not in st.session_state:
        st.session_state.memory = {
            "basic": ConversationBufferMemory(),
            "intermediate": ConversationBufferMemory(),
            "advanced": ConversationBufferMemory()
        }

# Display the messages for a particular level
def display_messages(tab):
    for message in st.session_state.messages[tab]:
        with st.chat_message(message['role']):
            st.write(message['content'])

def process_local_file(file_path, level):
    assistant = st.session_state["assistants"][level]
    if assistant.vector_store is None:
        if os.path.exists(file_path):
            assistant.feed(file_path)
        else:
            st.error(f"File not found for {level} level. Please check the file path.")

# New function to generate a unique key for caching
def generate_cache_key(level, step):
    return hashlib.md5(f"{level}_{step}".encode()).hexdigest()

# New function to check if cached content exists
def get_cached_content(cache_key):
    cache_dir = Path("content_cache")
    cache_file = cache_dir / f"{cache_key}.json"
    if cache_file.exists():
        with open(cache_file, "r") as f:
            return json.load(f)
    return None

# New function to save content to cache
def save_to_cache(cache_key, content):
    cache_dir = Path("content_cache")
    cache_dir.mkdir(exist_ok=True)
    cache_file = cache_dir / f"{cache_key}.json"
    with open(cache_file, "w") as f:
        json.dump(content, f)

# Modified personalized_learning function
@st.cache_resource
def personalized_learning(level):
    cache_key = generate_cache_key(level, 0)
    cached_content = get_cached_content(cache_key)
    
    if cached_content:
        return cached_content

    assistant = st.session_state["assistants"][level]

    relevant_information = assistant.get_relevent_information(f"Overview of {level}level AI concepts")

    prompt = f'''
    You are an AI tutor. You are teaching the {level.capitalize()} level of AI.
    Here's an overview of this level to guide your teaching:
    {relevant_information}
    
    Based on this information, teach the {level} level of the AI topic in a clear and concise manner. Generate about 500 words. 
    Include a brief example if appropriate. The example should be short, simple, and relevant to the concept.
    Make sure to adjust your explanations to the student's level of understanding.
    '''
    context = assistant.get_response_from_api(prompt)
    
    save_to_cache(cache_key, context)
    return context

def Understood(level, step, previous_content):
    assistant = st.session_state["assistants"][level]

    understood = st.radio(f"Did you understand? (Step {step})", 
                          ("still reading", "Yes", "No"), 
                          key=f"understood_radio_{level}_{step}")

    if understood == "Yes":
        st.write("Great! Let's dive deeper.")
        cache_key = generate_cache_key(level, step)
        cached_content = get_cached_content(cache_key)
        
        if cached_content:
            next_content = cached_content
        else:

            relevant_information = assistant.get_relevent_information(f"Advanced {level} level AI concepts")

            prompt = f'''
            Explain AI topic of {level} level for step {step}, in detail.
            The student has fully understood the previous explanation.
            Use this additional information to guide your explanation:
            {relevant_information}
            '''

            next_content = assistant.get_response_from_api(prompt)
            save_to_cache(cache_key, next_content)
        
        st.markdown(next_content)
        return "continue", step + 1, next_content

    elif understood == "No":
        st.write("Let's review this again with a simpler explanation.")
        cache_key = generate_cache_key(f"{level}_simpler", step)
        cached_content = get_cached_content(cache_key)
        
        if cached_content:
            simpler_explanation = cached_content
        else:

            relevant_infomation = assistant.get_relevent_information(f"Simple {level} level AI concepts")

            prompt = f'''
            The student didn't understand the following explanation about the AI topic of {level} level for step {step}:
            "{previous_content}"
            Please provide a simpler explanation of the same content, breaking it down further and using more accessible language.
            Use this additional information to guide your explanation:
            {relevant_infomation}
            '''

            simpler_explanation = assistant.get_response_from_api(prompt)
            save_to_cache(cache_key, simpler_explanation)
        
        st.markdown(simpler_explanation)
        return "continue", step + 1, simpler_explanation

    else:  # "still reading"
        return "wait", step + 1, previous_content

# Process user input and get chatbot response
def process_input(tab):
    memory = st.session_state.memory[tab]
    assistant = st.session_state["assistants"][tab]

    if prompt := st.chat_input(f"What can I do? ({tab} mode)"):
        with st.chat_message("user"):
            st.markdown(prompt)

        st.session_state.messages[tab].append({"role": "user", "content": prompt})

        conversation_history_str = memory.load_memory_variables({})["history"] if not no_memory else ""
        conversation_history = []
        
        if conversation_history_str:
            for line in conversation_history_str.split("\n"):
                if line.startswith("Human:"):
                    conversation_history.append({"role": "user", "content": line.replace("Human: ", "")})
                elif line.startswith("AI:"):
                    conversation_history.append({"role": "assistant", "content": line.replace("AI: ", "")})

        if limit_memory and len(conversation_history) > memory_limit * 2:
            conversation_history = conversation_history[-memory_limit * 2:]

        response = assistant.ask(prompt, context=conversation_history)

        save_response(tab, prompt, response)

        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages[tab].append({"role": "assistant", "content": response})

        if not no_memory:
            memory.save_context({"input": prompt}, {"output": response})

# Function to generate PDF of the chat history
def generate_pdf(conversation_history):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    for message in conversation_history:
        role = message["role"].capitalize()
        content = message["content"]
        
        # Set the role
        pdf.set_font("Arial", 'B', size=12)
        pdf.cell(200, 10, txt=f"{role}:", ln=True)
        
        # Set the content with UTF-8 characters
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=content, align="L")
        pdf.ln(5)

    pdf_output_path = "conversation_history.pdf"
    pdf.output(pdf_output_path)
    return pdf_output_path

# Main function
def main():
    st.title("AI Literature Assistant")

    # Initialize session state for assistants and messages
    initialize_session_state()

    # Load local files for each level
    basic_file_path = "D:\\FuseMachine\\DataSet_RAG\\FM_Basic.pdf"
    intermediate_file_path = "D:\\FuseMachine\\DataSet_RAG\\FM_Intermediate.pdf"
    advanced_file_path = "D:\\FuseMachine\\DataSet_RAG\\FM_Advanced.pdf"

    process_local_file(basic_file_path, "basic")
    process_local_file(intermediate_file_path, "intermediate")
    process_local_file(advanced_file_path, "advanced")

    # Page selection at the top
    page = st.selectbox("Choose a page", ["Home", "Personalized Learning"], key="page_selector")

    if page == "Home":
        # Sidebar for additional features
        with st.sidebar:
            st.header("Options")
            global no_memory, limit_memory, memory_limit

            # Memory and chat options
            no_memory = st.checkbox("No Memory", value=False)
            limit_memory = st.checkbox("Limit Memory", value=True, disabled=no_memory)
            memory_limit = st.number_input("Number of conversations to remember:", min_value=1, max_value=10, value=4, disabled=no_memory or not limit_memory)

            if st.button("New Chat"):
                st.session_state.messages = {"basic": [], "intermediate": [], "advanced": []}
                st.session_state.memory = {
                    "basic": ConversationBufferMemory(),
                    "intermediate": ConversationBufferMemory(),
                    "advanced": ConversationBufferMemory()
                }

            if st.button("Download Chat as PDF"):
                all_messages = []
                for tab in ["basic", "intermediate", "advanced"]:
                    all_messages.extend(st.session_state.messages[tab])
                pdf_path = generate_pdf(all_messages)
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(
                        label="Download PDF",
                        data=pdf_file,
                        file_name="conversation_history.pdf",
                        mime="application/pdf"
                    )

            # File uploader for the selected level
            selected_level = st.selectbox("Select Level for Upload", ["basic", "intermediate", "advanced"], key="level_selector")
            uploaded_file = st.file_uploader(f"Upload {selected_level.capitalize()} Level File", type=["pdf"], key=f"file_uploader_{selected_level}")

            if uploaded_file:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tf:
                    tf.write(uploaded_file.getbuffer())
                    file_path = tf.name
                
                with st.spinner(f"Uploading and processing {uploaded_file.name} for {selected_level} level"):
                    st.session_state["assistants"][selected_level].feed(file_path)
                
                os.remove(file_path)
                st.success(f"File uploaded and processed successfully for {selected_level} level!")

        # Display the content based on the selected page
        st.header("Welcome to the AI Literature Assistant")

        # Tabs for different levels
        tab1, tab2, tab3 = st.tabs(["Basic", "Intermediate", "Advanced"])

        with tab1:
            st.header("Basic Mode")
            display_messages("basic")
            process_input("basic")

        with tab2:
            st.header("Intermediate Mode")
            display_messages("intermediate")
            process_input("intermediate")

        with tab3:
            st.header("Advanced Mode")
            display_messages("advanced")
            process_input("advanced")

    elif page == "Personalized Learning":
        st.header("Personalized Learning Page")

        with st.sidebar:
            button = st.select_slider("", options=["None", "Start Generating"])

        if button == "Start Generating":
            with st.sidebar:
                selected_level = st.select_slider("Select Level", options=["Basic", "Intermediate", "Advanced"])

            initial_content = personalized_learning(selected_level.lower())
            st.markdown(initial_content)

            step = 1
            status = "continue"
            current_content = initial_content

            while status == "continue":
                status, step, current_content = Understood(selected_level.lower(), step, current_content)

if __name__ == "__main__":
    main()