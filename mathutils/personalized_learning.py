import datetime
import streamlit as st
import json
from dotenv import load_dotenv
from .retry_utils import generate_practice_problems_with_retries
from .course_structure import course_structure
from .dynamic_content import (
    generate_dynamic_content,
    store_content,
    retrieve_content,
    store_problems,
    retrieve_problems,
    extract_json_from_response,
    store_assessment,
    retrieve_assessment,
)
from .assessment import assessment_dashboard

load_dotenv()


def course_dashboard():
    st.title("Math Learning Dashboard")
    st.sidebar.header("Select a Topic")

    # Sidebar for selecting topic
    selected_topic = st.sidebar.selectbox(
        label="Choose a topic",
        options=["Select a topic"] + list(course_structure.keys()),
        # key="topic_selectbox",
    )

    if selected_topic and selected_topic != "Select a topic":
        levels = course_structure.get(selected_topic, {})

        st.sidebar.subheader(f"{selected_topic} - Course Levels")
        selected_level = st.sidebar.selectbox(
            "Choose your level", list(levels.keys()) if levels else []
        )

        if selected_level:
            lessons = levels[selected_level].get("lessons", [])

            st.sidebar.subheader(f"{selected_topic} - {selected_level} Lessons")
            selected_lesson = st.sidebar.selectbox(
                "Choose a lesson", lessons if lessons else []
            )

            if selected_lesson:
                st.header(f"Lesson: {selected_lesson}")

                regenerate_content = st.sidebar.button(
                    "Regenerate Content", key="regenerate_content"
                )

                # Retrieve content from the database each time
                explanation = retrieve_content(selected_topic, selected_lesson)
                if regenerate_content or explanation is None:
                    with st.spinner("Generating explanation..."):
                        explanation = generate_dynamic_content(
                            f"Explain {selected_lesson}."
                        )
                        store_content(selected_topic, selected_lesson, explanation)
                        st.sidebar.write("New content generated")
                else:
                    st.sidebar.write("Using cached content")

                st.write(explanation, unsafe_allow_html=True)

                st.write("### Practice Problems")

                # Retrieve problems specific to the topic, level, and lesson
                problems_json = retrieve_problems(
                    selected_topic, f"{selected_level}_{selected_lesson}"
                )

                if regenerate_content or problems_json is None:
                    with st.spinner("Generating practice problems..."):
                        problems_json = generate_practice_problems_with_retries(
                            explanation,
                            selected_topic,
                            f"{selected_level}_{selected_lesson}",
                        )
                        if problems_json:
                            store_problems(
                                selected_topic,
                                f"{selected_level}_{selected_lesson}",
                                json.dumps(problems_json),
                            )
                            st.sidebar.write("New problems generated")
                else:
                    st.sidebar.write("Using cached practice problems")

                if problems_json:
                    problems = (
                        json.loads(problems_json)
                        if isinstance(problems_json, str)
                        else problems_json
                    )

                    expander_state_key = (
                        f"{selected_topic}_{selected_level}_{selected_lesson}_expander"
                    )

                    with st.expander(
                        "Show Practice Problems",
                        expanded=st.session_state.get(expander_state_key, True),
                    ):
                        st.session_state[expander_state_key] = st.session_state.get(
                            expander_state_key, True
                        )
                        for i, problem in enumerate(problems.get("questions", [])):
                            st.markdown(
                                f":orange[**Question {i+1}:** {problem['question']}]",
                                unsafe_allow_html=True,
                            )
                            if st.button(
                                f"Show Answer to Q{i+1}", key=f"show_answer_{i+1}"
                            ):
                                st.markdown(f"**Answer:** {problem['solution']}")

                else:
                    st.write(
                        "Practice sets not available! Please try generating again."
                    )

                if st.button("New Practice Sets", key="new_practice_sets"):
                    with st.spinner("Generating new practice problems..."):
                        # Refresh explanation from the database before generating new problems
                        explanation = retrieve_content(selected_topic, selected_lesson)
                        problems_json = generate_practice_problems_with_retries(
                            explanation,
                            selected_topic,
                            f"{selected_level}_{selected_lesson}",
                        )
                        if problems_json:
                            store_problems(
                                selected_topic,
                                f"{selected_level}_{selected_lesson}",
                                json.dumps(problems_json),
                            )
                            st.empty()
                            st.rerun()

                st.write("### Assessment")
                assessment = levels[selected_level].get(
                    "assessment", "No assessment available"
                )

                # Add session state to track if the assessment expander should stay open
                assessment_expander_key = (
                    f"{selected_topic}_{selected_level}_assessment_expander"
                )
                st.session_state.setdefault(assessment_expander_key, True)

                if st.button(f"Take {assessment}", key="take_assessment"):
                    st.session_state[assessment_expander_key] = True

                if st.session_state[assessment_expander_key]:
                    assessment_dashboard(
                        selected_topic, selected_level, selected_lesson
                    )
