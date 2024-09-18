import streamlit as st

# Set page configuration once
st.set_page_config(
    page_title="AI Tutor", initial_sidebar_state="collapsed", layout="wide"
)

st.title("Welcome !!!")

# Store the previous selection in session state
if "prev_option" not in st.session_state:
    st.session_state.prev_option = None

# Select box to choose between options
option = st.selectbox(
    "Choose an option:",
    ["Math Learning & QA", "MoA Code Debugging", "AI QA", "MoA AI QA"],
)

# If a new option is selected, reset the session state
if st.session_state.prev_option != option:
    st.session_state.clear()
    st.session_state.prev_option = option

# Logic to redirect to the chosen page
if option == "Math Learning & QA":
    st.session_state.page = "app1"
elif option == "MoA Code Debugging":
    st.session_state.page = "app2"
elif option == "MoA AI QA":
    st.session_state.page = "ai_qa"
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
    elif st.session_state.page == "ai_qa":
        exec(open("./pages/page2/ai_qa.py").read())
    elif st.session_state.page == "app3":
        exec(open("./pages/page3/app3.py").read())
    elif st.session_state.page == "app4":
        exec(open("./pages/page4/app4.py").read())
