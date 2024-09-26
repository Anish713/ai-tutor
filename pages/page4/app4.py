import streamlit as st
import tempfile
import os
from langchain.memory import ConversationBufferMemory
from fpdf import FPDF
from RAG.RAG import rag


st.session_state.step = 0

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
            st.markdown(message['content'])


def process_local_file(file_path, level):
    assistant = st.session_state["assistants"][level]
    if assistant.vector_store is None:
        if os.path.exists(file_path):
            assistant.feed(file_path)
        else:
            st.error(f"File not found for {level} level. Please check the file path.")


@st.cache_resource
def personalized_learning(level):
    assistant = st.session_state["assistants"][level]
    prompt = f'''
    You are an AI tutor. You are teaching the {level.capitalize()} level of AI.
    Here's an overview of this level to guide your teaching:
    Teach the {level} level of the AI topic in a clear and concise manner. Generate about 500 words. 
    Include a brief example if appropriate. The example should be short, simple, and relevant to the concept.
    Make sure to adjust your explanations to the student's level of understanding.
    '''
    #st.write("Generating detailed content...")
    context = assistant.get_response_from_api(prompt)
    return context

def Understood(level, step):
    assistant = st.session_state["assistants"][level]

    understood = st.radio(f"Did you understand? (Step {step})", ("still reading", "Yes", "No"), key=f"understood_radio_{level}_{step}")

    if understood == "Yes":
        st.write("Great! Let's dive deeper.")
        next_content = assistant.get_response_from_api(f'''
        Explain AI topic of {level} level for step {step}, in detail.
        The student has fully understood the previous explanation.
        ''')
        st.markdown(next_content)
        Understood(level, step + 1)
    elif understood == "No":
        st.write("Let's review this again with a simpler explanation.")
        simpler_explanation = assistant.get_response_from_api(f'''
        Explain AI topic of {level} level for step {step}, but in a simpler way.
        The student hasn't fully understood the previous explanation.
        ''')
        st.write(simpler_explanation)
        Understood(level, step)



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
    basic_file_path = "D:\\FuseMachine\\DataSet_RAG\\Data_basic.pdf"
    intermediate_file_path = "D:\\FuseMachine\\DataSet_RAG\\Data_intermediate.pdf"
    advanced_file_path = "D:\\FuseMachine\\DataSet_RAG\\Data_advance.pdf"

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
            button = st.select_slider("", options = ["None", "Start Generating"])

        if button == "Start Generating":

            with st.sidebar:
                selected_level = st.select_slider("Select Level", options = ["Basic", "Intermediate", "Advanced"])

            if selected_level == "Basic":
                initial_content = personalized_learning("basic")
                st.markdown(initial_content)
                Understood("basic", 1)

            elif selected_level == "Intermediate":
                initial_content = personalized_learning("intermediate")
                st.markdown(initial_content)
                Understood("intermediate", 1)

            elif selected_level == "Advanced":
                initial_content = personalized_learning("advanced")
                st.markdown(initial_content)
                Understood("advanced", 1)

if __name__ == "__main__":
    main()