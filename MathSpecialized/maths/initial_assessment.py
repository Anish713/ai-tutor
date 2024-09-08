import streamlit as st


def initial_assessment():
    st.title("Initial Assessment")
    st.write("This assessment will help us determine your current level.")

    # simple static assessment with a few questions
    score = 0
    if st.radio("Question 1: What is 2 + 2?", ["3", "4", "5"]) == "4":
        score += 1
    if st.radio("Question 2: What is the square root of 16?", ["2", "4", "8"]) == "4":
        score += 1

    st.write(f"Your score: {score}/2")

    if score == 2:
        st.success("You are ready for the Intermediate level!")
    else:
        st.info("We recommend starting with the Beginner level.")

    # Store this result in session state or a database for future reference for personalization
