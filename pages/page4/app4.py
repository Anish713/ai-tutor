import streamlit as st
import tempfile
import os
from langchain.memory import ConversationBufferMemory
from fpdf import FPDF
from RAG.RAG import rag

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

# Function to handle Personalized QA (currently blank)
def personalized_learning(level):
    assistant = st.session_state["assistants"][level]
    st.subheader(f"Personalized Learning for {level.capitalize()} Level")

    # Fetch the dynamically generated level description from the assistant's database
    level_description = assistant.get_level_description()

    # Include the level description in the prompt
    prompt = f'''
    You are an AI tutor. You are teaching the {level.capitalize()} level of AI.
    Here's an overview of this level to guide your teaching:

    "{level_description}"

    Teach the {level} level of the AI topic in a clear and concise manner. Focus on one concept at a time. 
    Include a brief example if appropriate. The example should be short, simple, and relevant to the concept.
    Make sure to adjust your explanations to the student's level of understanding.
    '''
    
    # Display the prompt for debugging purposes (optional)
    #st.write("Prompt being used for content generation:")
    #st.markdown(f"```{prompt}```")

    # Generating the personalized content
    st.write("Generating detailed content...")
    context = assistant.get_response_from_api(prompt)
    st.markdown(context)

    

    understood = st.selectbox("Did you understand this step?", ("choose", "Yes", "No"), index = 0)

    if understood == "Yes":
        #yes_ans = context + f"The student has understood the step you recently taught. Now dive deep into this topic and generate another content related to this level topic."
        st.write("Great! Moving to the next step.")
        next_explanation = assistant.get_response_from_api(f"dive deeper on each topics of {level_description}")
        st.write(next_explanation)
    elif understood == "No":
        st.write("Let's review this step again with a simpler explanation.")
        simpler_explanation = assistant.get_response_from_api(f'''
            Explain this AI topic of {level} level again, but in a simpler way.
            The student hasn't fully understood the previous explanation.
        ''')
        st.write(simpler_explanation)
    else:
        st.write("Please select an option to continue.")
    
# Main function
def main():
    st.title("AI Literature Assistant")

    # Initialize session state for assistants and messages
    initialize_session_state()

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
        # Hide the sidebar by not rendering it
        #st.write("This is a placeholder for the Personalized QA page.")
        st.header("Personalized Learning Page")
        #st.subheader("Personalized Learning")
        with st.sidebar:
            selected_level = st.selectbox("Select Level for Personalized Learning", ["basic", "intermediate", "advanced"])
        
            # Call personalized QA function (currently blank)
        personalized_learning(selected_level)

if __name__ == "__main__":
    main()