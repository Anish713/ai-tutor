import streamlit as st
from maths.personalized_learning import course_dashboard
from maths.initial_assessment import initial_assessment
from maths.dynamic_content import create_db


def math_qa():
    st.title("Math QA")
    st.write("Ask your math questions here.")
    # Implement the existing Math QA functionality here


def main():
    st.sidebar.title("Math Learning App")

    create_db()

    app_mode = st.sidebar.selectbox(
        "Choose the mode",
        ["Math Specialization Learning", "Math QA", "Initial Assessment"],
    )

    if app_mode == "Math QA":
        math_qa()
    elif app_mode == "Math Specialization Learning":
        course_dashboard()
    elif app_mode == "Initial Assessment":
        initial_assessment()


if __name__ == "__main__":
    main()
