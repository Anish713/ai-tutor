import streamlit as st
import json
from config.config import *
from streamlit_ace import st_ace


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

set_moa_agent()

# Sidebar for configuration
with st.sidebar:
    st.title("MOA Configuration")
    with st.form("Agent Configuration", border=False):
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
                    main_model=new_main_model,
                    cycles=new_cycles,
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

# Main app layout
st.header("Mixture of Agents", anchor=False)

with st.expander("Current MOA Configuration", expanded=False):
    st.markdown(f"**Main Model**: ``{st.session_state.main_model}``")
    st.markdown(f"**Main Model Temperature**: ``{st.session_state.main_temp:.1f}``")
    st.markdown(f"**Layers**: ``{st.session_state.cycles}``")
    st.markdown(f"**Layer Agents Config**:")
    new_layer_agent_config = st_ace(
        value=json.dumps(st.session_state.layer_agent_config, indent=2),
        language="json",
        placeholder="Layer Agent Configuration (JSON)",
        show_gutter=False,
        wrap=True,
        readonly=True,
        auto_update=True,
    )

# Chat interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if query := st.chat_input("Ask a question"):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.write(query)

    moa_agent: MOAgent = st.session_state.moa_agent
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        ast_mess = stream_response(moa_agent.chat(query, output_format="json"))
        response = st.write_stream(ast_mess)

    st.session_state.messages.append({"role": "assistant", "content": response})

# if st.button("Back"):
#     st.session_state.page = None
#     exec(open("../main.py").read())
