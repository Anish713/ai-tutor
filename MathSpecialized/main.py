# main_app.py

import streamlit as st
from mathutils.personalized_learning import course_dashboard
from mathutils.initial_assessment import initial_assessment

def math_qa():
    st.title("Math QA")
    st.write("Ask your math questions here.")
    # Implement the existing Math QA functionality here

def main():
    st.sidebar.title("Math Learning App")
    app_mode = st.sidebar.selectbox("Choose the mode", ["Specialized Math Learning", "Math QA", "Initial Assessment"])
    
    if app_mode == "Math QA":
        math_qa()
    elif app_mode == "Specialized Math Learning":
        course_dashboard()
    elif app_mode == "Initial Assessment":
        initial_assessment()

if __name__ == "__main__":
    main()
