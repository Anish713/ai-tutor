import json
import datetime
import streamlit as st
import sqlite3
import streamlit.components.v1 as components
from .retry_utils import (
    generate_assessment_with_retries,
    generate_feedback,
)
from .dynamic_content import (
    generate_dynamic_content,
    store_content,
    retrieve_content,
    store_assessment,
    retrieve_assessment,
    store_user_answers,
    extract_json_from_response,
)

DB_PATH = "generated_content.db"


def assessment_dashboard(selected_topic, selected_level, selected_lesson):
    st.header(f"Assessment: {selected_lesson}")

    # Retrieve assessment from database
    assessment_json = retrieve_assessment(
        selected_topic, f"{selected_level}_{selected_lesson}"
    )

    if assessment_json is None:
        with st.spinner("Generating assessment..."):
            assessment_json = generate_assessment_with_retries(
                selected_topic, selected_level, selected_lesson
            )
            store_assessment(
                selected_topic,
                f"{selected_level}_{selected_lesson}",
                json.dumps(assessment_json),
            )
            st.rerun()

    if isinstance(assessment_json, dict):
        assessment = assessment_json
    elif isinstance(assessment_json, str):
        assessment = json.loads(assessment_json)
    else:
        raise ValueError("Invalid type for assessment_json")

    questions = assessment["questions"]
    answers = []

    if "start_time" not in st.session_state:
        st.session_state["start_time"] = datetime.datetime.now()

    for i, question in enumerate(questions):
        question_key = f"question_{i}_start_time"
        if question_key not in st.session_state:
            st.session_state[question_key] = datetime.datetime.now()

        st.markdown(f":orange[**Question {i+1}:** {question['question']}]")
        options = question["options"]
        answer = st.selectbox(
            f"Select an answer for Q{i+1}", options, key=f"answer_{i+1}"
        )
        answers.append(answer)

    # Submit the assessment
    if st.button("Submit"):
        score = 0
        correct_answers = []
        wrong_answers = []

        for i, question in enumerate(questions):
            if answers[i] == question["correct_answer"]:
                score += 1
                correct_answers.append(i + 1)
            else:
                wrong_answers.append(i + 1)

        total_time = (
            datetime.datetime.now() - st.session_state["start_time"]
        ).total_seconds()

        store_user_answers(
            selected_topic,
            selected_level,
            answers,
            score,
        )

        if score >= 1:  # change threshold later
            st.success(f"**Congratulations! You scored {score}/10**", icon="🔥")
            mycode = "<script>alert('Check your feedback😀 Then, You may move to next lesson. Good Luck! ')</script>"
            components.html(mycode, height=0, width=0)
            st.info("Check Feedback below for wrong Answers, if any.")
            st.markdown("# Feedback for Wrong Answers:")
            st.write("## :green[**Correctly Answered:**]")
            for i in correct_answers:
                st.write(
                    f"""➡️ You have correctly answered **Question {i}: :green[{questions[i-1]['correct_answer']}]** ✅"""
                )

            st.write("## :red[**Wrongly Answered:**]")
            for i in wrong_answers:
                st.markdown(f":red[**Question {i}:**] {questions[i-1]['question']}")
                st.write(
                    f"""➡️ You answered: :red[{answers[i-1]}] ❌. Correct Answer is :green[**{questions[i-1]['correct_answer']}**] ✔️"""
                )
                with st.spinner("Generating Feedback..."):
                    feedback = generate_feedback(
                        question=questions[i - 1]["question"],
                        student_answer=answers[i - 1],
                        actual_answer=questions[i - 1]["correct_answer"],
                    )
                    st.info(f":green[**Feedback:**] {feedback}", icon="🚨")
                    # st.markdown(f":green[**🚨 Feedback:**] :blue-background[{feedback}]")
                    st.divider()

        else:
            st.write(f"You scored {score}/10 😥.")
            st.error(
                ":red-background[**Please revise the provided resources 📖 and Try again...🔁**]"
            )
            st.info("Pro Tip: Use Chatbot in sidebar to clear your confusions😎")

    # option to generate a new quiz
    if st.button("New Quiz"):
        with st.spinner("Generating a new quiz..."):
            assessment_json = generate_assessment_with_retries(
                selected_topic, selected_level, selected_lesson
            )
            store_assessment(
                selected_topic,
                f"{selected_level}_{selected_lesson}",
                json.dumps(assessment_json),
            )
            st.rerun()
