import json
import datetime
import sqlite3
import streamlit as st
from .dynamic_content import (
    generate_dynamic_content,
    extract_json_from_response,
    retrieve_content,
    generate_dynamic_content_github,
    generate_dynamic_content_groq,
)
from dotenv import load_dotenv

load_dotenv()


def generate_practice_problems_with_retries(
    explanation, selected_topic, selected_level
):
    max_retries = 1
    temperatures = [0.7, 0.3, 0.9]
    groq_models = [
        "llama-3.2-11b-text-preview",
        "Llama-3.1-70b-Versatile",
        "Llama-3.1-8b-Instant",
        "llama3-8b-8192",
        "gemma2-9b-it",
        "mixtral-8x7b-32768",
    ]
    github_models = ["gpt-4o-mini", "gpt-4o"]

    def try_generate(model_type, model_name, temperature):
        try:
            # st.write(
            #     f"Attempting generation with {model_type} model '{model_name}' at temperature {temperature}"
            # )
            problems_response = generate_dynamic_content(
                f"""Based on the following lesson content, generate 2 simple, 2 intermediate, and 2 complex questions along with their respective answers for the {selected_level} level in the topic {selected_topic}. Strictly use the given JSON Format below as your response format.
                
                # Lesson Content: {explanation}
                
                # JSON Format:
                {{
                    "questions": [
                        {{
                            "difficulty": "simple",
                            "question": "Simple question 1",
                            "solution": "solution 1"
                        }},
                        {{
                            "difficulty": "simple",
                            "question": "Simple question 2",
                            "solution": "solution 2"
                        }},
                        {{
                            "difficulty": "intermediate",
                            "question": "Intermediate question 1",
                            "solution": "solution 1"
                        }},
                        {{
                            "difficulty": "intermediate",
                            "question": "Intermediate question 2",
                            "solution": "solution 2"
                        }},
                        {{
                            "difficulty": "complex",
                            "question": "Complex question 1",
                            "solution": "solution 1"
                        }},
                        {{
                            "difficulty": "complex",
                            "question": "Complex question 2",
                            "solution": "solution 2"
                        }}
                    ]
                }}""",
                model_type=model_type,
                model_name=model_name,
                temperature=temperature,
            )

            problems_json = extract_json_from_response(problems_response)
            return problems_json
        except Exception as e:
            st.error(f"Error occurred: {str(e)}. Retrying...")

    model_index = 0
    attempts = 0
    temperature_index = 0
    while model_index < len(groq_models):
        model_name = groq_models[model_index]
        temperature = temperatures[temperature_index]
        problems_json = try_generate("groq", model_name, temperature)
        if problems_json:
            return problems_json
        attempts += 1
        temperature_index += 1
        if temperature_index >= len(temperatures):
            temperature_index = 0
            model_index += 1
        if attempts >= max_retries * len(temperatures) * len(groq_models):
            break

    st.error(
        "Maximum retry attempts reached with Groq models. Switching to GitHub models."
    )

    model_index = 0
    attempts = 0
    temperature_index = 0
    while model_index < len(github_models):
        model_name = github_models[model_index]
        temperature = temperatures[temperature_index]
        problems_json = try_generate("github", model_name, temperature)
        if problems_json:
            return problems_json
        attempts += 1
        temperature_index += 1
        if temperature_index >= len(temperatures):
            temperature_index = 0
            model_index += 1
        if attempts >= max_retries * len(temperatures) * len(github_models):
            break

    # st.rerun()

    st.error("Maximum retry attempts reached with all models.")

    st.error("Failed to generate practice problems after several attempts.")
    return None


def generate_assessment_with_retries(selected_topic, selected_level, selected_lesson):
    max_retries = 1
    temperatures = [0.7, 0.4, 0.9]
    groq_models = [
        "llama-3.2-11b-text-preview",
        "Llama-3.1-70b-Versatile",
        "Llama-3.1-8b-Instant",
        "llama3-8b-8192",
        "gemma2-9b-it",
        "mixtral-8x7b-32768",
    ]
    github_models = ["gpt-4o-mini", "gpt-4o"]

    def try_generate(model_type, model_name, temperature):
        try:
            # st.write(
            #     f"Attempting generation with {model_type} model '{model_name}' at temperature {temperature}"
            # )
            assessment_response = generate_dynamic_content(
                f"""Based on the following lesson content, generate exactly 10 multiple-choice questions along with their respective answers for the {selected_level} level in the topic {selected_topic}. Make sure that only one option is correct while other options are wrong but seems quite similar to the actual option. Strictly use the given JSON Format below as your response format.
                
                # Lesson Content: {retrieve_content(selected_topic, selected_lesson)}
                
                # JSON Format:
                {{
                    "questions": [
                        {{
                            "question": "Question 1",
                            "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                            "correct_answer": "Correct option for  Question 1"

                        }},
                        {{
                            "question": "Question 2",
                            "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                            "correct_answer": "Correct option for Question 2"
                        }},
                        ...
                    ]
                }}""",
                model_type=model_type,
                model_name=model_name,
                temperature=temperature,
            )

            assessment_json = extract_json_from_response(assessment_response)
            return assessment_json
        except Exception as e:
            st.error(f"Error occurred: {str(e)}. Retrying...")

    model_index = 0
    attempts = 0
    temperature_index = 0
    while model_index < len(groq_models):
        model_name = groq_models[model_index]
        temperature = temperatures[temperature_index]
        assessment_json = try_generate("groq", model_name, temperature)
        if assessment_json:
            return assessment_json
        attempts += 1
        temperature_index += 1
        if temperature_index >= len(temperatures):
            temperature_index = 0
            model_index += 1
        if attempts >= max_retries * len(temperatures) * len(groq_models):
            break

    # st.error(
    #     "Maximum retry attempts reached with Groq models. Switching to GitHub models."
    # )

    model_index = 0
    attempts = 0
    temperature_index = 0
    while model_index < len(github_models):
        model_name = github_models[model_index]
        temperature = temperatures[temperature_index]
        assessment_json = try_generate("github", model_name, temperature)
        if assessment_json:
            return assessment_json
        attempts += 1
        temperature_index += 1
        if temperature_index >= len(temperatures):
            temperature_index = 0
            model_index += 1
        if attempts >= max_retries * len(temperatures) * len(github_models):
            break

    st.error("Maximum retry attempts reached with all models.")

    st.error("Failed to generate assessment after several attempts.")
    st.error("Please retry generating again...")
    return None


def generate_feedback(question, student_answer, actual_answer):
    # Construct the prompt to generate feedback
    prompt = f"""# Information:
    - Question: {question}
    - Student's Answer: {student_answer}
    - Correct Answer: {actual_answer}.
    
Based on the above information, provide a feedback explaining the potential misconceptions in the student's answer and short clarification to right answer. Aim to make feedback as short and useful as possible."""
    # First, try using GitHub models
    try:
        print(f"Generating feedback using GitHub models.")
        return generate_dynamic_content_github(
            query=prompt,
            model_name="gpt-4o-mini",
            temperature=0.5,
        )
    except Exception as e_github:
        print(f"Error using GitHub model 'gpt-4o-mini': {e_github}")
        try:
            return generate_dynamic_content_github(
                query=prompt,
                model_name="gpt-4o",
                temperature=0.5,
            )
        except Exception as e_github_fallback:
            print(f"Error using GitHub model 'gpt-4o': {e_github_fallback}")
            # Use Groq models if GitHub models fail
            try:
                print(f"Generating feedback using Groq models.")
                return generate_dynamic_content_groq(
                    query=prompt, model_name="Llama-3.1-8b-Instant", temperature=0.5
                )
            except Exception as e_groq:
                print(f"Error using Groq model: {e_groq}")
                return "Error generating feedback with available models."
