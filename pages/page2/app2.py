import streamlit as st
import json
from config.config import (
    valid_model_names,
    default_config,
    layer_agent_config_def,
    rec_config,
    layer_agent_config_rec,
    stream_response,
    set_moa_agent,
)
from moa.agent import MOAgent
from streamlit_ace import st_ace

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "first_input" not in st.session_state:
    st.session_state.first_input = True  # Flag to determine if it's the first input

set_moa_agent()

# Sidebar for configuration
with st.sidebar:
    st.title("MOA Configuration")
    with st.form("Agent Configuration", clear_on_submit=False):
        if st.form_submit_button("Use Recommended Config"):
            try:
                set_moa_agent(
                    main_model=rec_config["main_model"],
                    cycles=rec_config["cycles"],
                    layer_agent_config=layer_agent_config_rec,
                    override=True,
                )
                st.session_state.messages = []
                st.success("Configuration updated successfully!")
            except json.JSONDecodeError:
                st.error(
                    "Invalid JSON in Layer Agent Configuration. Please check your input."
                )
            except Exception as e:
                st.error(f"Error updating configuration: {str(e)}")

        new_main_model = st.selectbox(
            "Select Main Model",
            options=valid_model_names,
            index=valid_model_names.index(st.session_state.main_model),
        )

        new_cycles = st.number_input(
            "Number of Layers", min_value=1, max_value=10, value=st.session_state.cycles
        )

        main_temperature = st.number_input(
            label="Main Model Temperature",
            value=0.1,
            min_value=0.0,
            max_value=1.0,
            step=0.1,
        )

        tooltip = "Agents in the layer agent configuration run in parallel _per cycle_."
        st.markdown("Layer Agent Config", help=tooltip)
        new_layer_agent_config = st_ace(
            value=json.dumps(st.session_state.layer_agent_config, indent=2),
            language="json",
            placeholder="Layer Agent Configuration (JSON)",
            show_gutter=False,
            wrap=True,
            auto_update=True,
        )

        if st.form_submit_button("Update Configuration"):
            try:
                new_layer_config = json.loads(new_layer_agent_config)
                set_moa_agent(
                    main_model=(
                        new_main_model
                        if new_main_model is not None
                        else default_config["main_model"]
                    ),
                    cycles=int(new_cycles),  # type: ignore
                    layer_agent_config=new_layer_config,
                    main_model_temperature=main_temperature,
                    override=True,
                )
                st.session_state.messages = []
                st.success("Configuration updated successfully!")
            except json.JSONDecodeError:
                st.error(
                    "Invalid JSON in Layer Agent Configuration. Please check your input."
                )
            except Exception as e:
                st.error(f"Error updating configuration: {str(e)}")

# # Main app layout
# st.header("Mixture of Agents", anchor=False)

# First input with code issues description
if st.session_state.first_input:
    with st.form("chat_input_form"):
        code = st.text_area("Code", key="code_input")
        error_message = st.text_area("Error Message", key="error_input")
        st.text_area("Description", key="description_input")

        if st.form_submit_button("Submit"):
            if not code or not error_message:
                st.warning("Code and Error Message are required for the first input.")
            else:
                prompt = f"""Help me debug the code by finding the issue and providing correctly working code. 
Provided Information: 
# CODE:
{code}

# Error Message:
{error_message}

# Description:
{st.session_state.description_input}
"""
                st.session_state.first_input = False
                st.session_state.messages.append({"role": "user", "content": prompt})
                moa_agent: MOAgent = st.session_state.moa_agent
                response = "".join(moa_agent.chat(prompt))
                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )
                st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Follow-up questions after the first input
if not st.session_state.first_input:
    if query := st.chat_input("Ask a follow-up question"):
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.write(query)

        moa_agent: MOAgent = st.session_state.moa_agent
        response = "".join(moa_agent.chat(query))
        with st.chat_message("assistant"):
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

# Option to start a new conversation
with st.form("new_conversation"):
    if st.form_submit_button("Start New Conversation"):
        st.session_state.messages = []
        st.session_state.first_input = True
        st.rerun()
