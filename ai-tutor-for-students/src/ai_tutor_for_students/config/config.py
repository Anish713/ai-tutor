import copy
import json
from typing import Iterable

import streamlit as st

from moa.agent import MOAgent
from moa.agent.moa import ResponseChunk

valid_model_names = [
    "llama3-70b-8192",
    "llama3-8b-8192",
    "gemma-7b-it",
    "gemma2-9b-it",
    "mixtral-8x7b-32768",
]

# Default configuration
default_config = {
    "main_model": "llama3-70b-8192",
    "cycles": 3,
    "layer_agent_config": {},
}

layer_agent_config_def = {
    "layer_agent_1": {
        "system_prompt": "Think through your response step by step. {helper_response}",
        "model_name": "llama3-8b-8192",
    },
    "layer_agent_2": {
        "system_prompt": "Respond with a thought and then your response to the question. {helper_response}",
        "model_name": "gemma-7b-it",
        "temperature": 0.7,
    },
    "layer_agent_3": {
        "system_prompt": "You are an expert at logic and reasoning. Always take a logical approach to the answer. {helper_response}",
        "model_name": "llama3-8b-8192",
    },
}

# Recommended Configuration

rec_config = {"main_model": "llama3-70b-8192", "cycles": 2, "layer_agent_config": {}}

layer_agent_config_rec = {
    "layer_agent_1": {
        "system_prompt": "Think through your response step by step. {helper_response}",
        "model_name": "llama3-8b-8192",
        "temperature": 0.1,
    },
    "layer_agent_2": {
        "system_prompt": "Respond with a thought and then your response to the question. {helper_response}",
        "model_name": "llama3-8b-8192",
        "temperature": 0.2,
    },
    "layer_agent_3": {
        "system_prompt": "You are an expert at logic and reasoning. Always take a logical approach to the answer. {helper_response}",
        "model_name": "llama3-8b-8192",
        "temperature": 0.4,
    },
    "layer_agent_4": {
        "system_prompt": "You are an expert planner agent. Create a plan for how to answer the human's query. {helper_response}",
        "model_name": "mixtral-8x7b-32768",
        "temperature": 0.5,
    },
}


def stream_response(messages: Iterable[ResponseChunk]):
    layer_outputs = {}
    for message in messages:
        if message["response_type"] == "intermediate":
            layer = message["metadata"]["layer"]
            if layer not in layer_outputs:
                layer_outputs[layer] = []
            layer_outputs[layer].append(message["delta"])
        else:  ###comment this 'else' part to not display each layer agents outputs
            # Display accumulated layer outputs
            for layer, outputs in layer_outputs.items():
                st.write(f"Layer {layer}")
                cols = st.columns(len(outputs))
                for i, output in enumerate(outputs):
                    with cols[i]:
                        st.expander(label=f"Agent {i+1}", expanded=False).write(output)

            #     # #Clear layer outputs for the next iteration
            layer_outputs = {}

            # Yield the main agent's output
            yield message["delta"]


def set_moa_agent(
    main_model: str = default_config["main_model"],
    cycles: int = default_config["cycles"],
    layer_agent_config: dict[dict[str, any]] = copy.deepcopy(layer_agent_config_def),
    main_model_temperature: float = 0.1,
    override: bool = False,
):
    if override or ("main_model" not in st.session_state):
        st.session_state.main_model = main_model
    else:
        if "main_model" not in st.session_state:
            st.session_state.main_model = main_model

    if override or ("cycles" not in st.session_state):
        st.session_state.cycles = cycles
    else:
        if "cycles" not in st.session_state:
            st.session_state.cycles = cycles

    if override or ("layer_agent_config" not in st.session_state):
        st.session_state.layer_agent_config = layer_agent_config
    else:
        if "layer_agent_config" not in st.session_state:
            st.session_state.layer_agent_config = layer_agent_config

    if override or ("main_temp" not in st.session_state):
        st.session_state.main_temp = main_model_temperature
    else:
        if "main_temp" not in st.session_state:
            st.session_state.main_temp = main_model_temperature

    cls_ly_conf = copy.deepcopy(st.session_state.layer_agent_config)

    if override or ("moa_agent" not in st.session_state):
        st.session_state.moa_agent = MOAgent.from_config(
            main_model=st.session_state.main_model,
            cycles=st.session_state.cycles,
            layer_agent_config=cls_ly_conf,
            temperature=st.session_state.main_temp,
        )

    del cls_ly_conf
    del layer_agent_config