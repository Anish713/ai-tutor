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
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for message in conversation_history:
        role = message["role"].capitalize()
        content = message["content"]
        pdf.cell(200, 10, txt=f"{role}: {content}", ln=True)

    pdf_output_path = "conversation_history.pdf"
    pdf.output(pdf_output_path)
    return pdf_output_path

# Function to handle Personalized QA (currently blank)
def personalized_learning(level):
    assistant = st.session_state["assistants"][level]
    st.subheader(f"Personalized Learning for {level.capitalize()} Level")

    # Use the assistant to get context
    query = "Generate detailed AI literature content for this level with comprehensive information."
    
    # Retrieve context (this assumes `ask` can be used for context retrieval as well)
    st.write("Generating detailed content...")
    context = assistant.ask(query)  # Adjust this line based on how context is retrieved in your `rag` class

    # Function to generate multi-page content
    def generate_multichunk_content(query, context, chunk_size=2000):
        full_content = ""
        start = 0
        while start < len(query):
            end = min(start + chunk_size, len(query))
            chunk = query[start:end]
            prompt_with_context = f"{context}\n\nContent Request: {chunk}"
            response = assistant.ask(prompt_with_context)
            full_content += response + "\n\n---\n\n"
            start = end
        return full_content

    # Generate content automatically based on context and generate multi-page content
    content = generate_multichunk_content(query, context)
    
    # Display the content
    st.write(content)

    # Optionally, you can add pagination or formatting here if needed
    st.write("### Detailed Content:")
    st.write("Here you can add functionality to paginate or format detailed content.")

    # Generate content automatically based on context and generate multi-page content
    query = "Generate detailed AI literature content for this level with comprehensive information."
    st.write("Generating detailed content...")
    
    content = generate_multichunk_content(query, context)
    
    # Display the content
    st.write(content)

    # Optionally, you can add pagination or formatting here if needed
    st.write("### Detailed Content:")
    st.write("Here you can add functionality to paginate or format detailed content.")



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
