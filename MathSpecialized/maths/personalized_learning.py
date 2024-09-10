import streamlit as st
from .course_structure import course_structure
from .dynamic_content import generate_dynamic_content


def course_dashboard():
    st.title("Math Learning Dashboard")

    st.sidebar.header("Select a Topic")
    selected_topic = st.sidebar.selectbox(
        "Choose a topic", ["Select a topic"] + list(course_structure.keys())
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

                with st.spinner("Generating explanation..."):
                    explanation = "".join(
                        generate_dynamic_content(
                            f"Explain {selected_lesson} in brief. Express any present equations as LaTeX code instead of direct equations."
                        )
                    )
                    st.write(explanation, unsafe_allow_html=True)

                practice_problems = levels[selected_level].get("practice_problems", [])
                assessment = levels[selected_level].get(
                    "assessment", "No assessment available"
                )

                st.write("### Practice Problems")
                for problem_set in practice_problems:
                    st.write(f"- {problem_set}")

                st.write("### Assessment")
                if st.button(f"Take {assessment}"):
                    st.write("Assessment functionality will be implemented here.")
