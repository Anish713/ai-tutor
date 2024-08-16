import streamlit as st

# Set page configuration once
st.set_page_config(
    page_title="AI Tutor", initial_sidebar_state="collapsed", layout="wide"
)

st.title("Welcome !!!")

# Select box to choose between options
option = st.selectbox(
    "Choose an option:",
    ["Math QA", "AI QA & Code Debugging", "Code Debugging", "AI QA"],
    # [ "AI QA & Code Debugging", "Math QA", "Code Debugging", "AI QA"],
)

# Logic to redirect to the chosen page
if option == "Math QA":
    st.session_state.page = "app1"
elif option == "AI QA & Code Debugging":
    st.session_state.page = "app2"
elif option == "Code Debugging":
    st.session_state.page = "app3"
elif option == "AI QA":
    st.session_state.page = "app4"

# Conditionally run the respective script based on the selection
if "page" in st.session_state:
    if st.session_state.page == "app1":
        exec(open("./pages/page1/app1.py").read())

    elif st.session_state.page == "app2":
        exec(open("./pages/page2/app2.py").read())

    elif st.session_state.page == "app3":
        exec(open("./pages/page3/app3.py").read())

    elif st.session_state.page == "app4":
        exec(open("./pages/page4/app4.py").read())
