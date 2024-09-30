import sqlite3
from openai import OpenAI
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from mathutils.mathutils import get_response_from_api
import json
import os

DB_PATH = "generated_content.db"
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def create_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute(
            """CREATE TABLE IF NOT EXISTS content
                     (topic TEXT, lesson TEXT, content TEXT, PRIMARY KEY (topic, lesson))"""
        )
        c.execute(
            """CREATE TABLE IF NOT EXISTS problems
                     (topic TEXT, level TEXT, problems TEXT, PRIMARY KEY (topic, level))"""
        )
        c.execute(
            """CREATE TABLE IF NOT EXISTS assessments
                     (topic TEXT, level TEXT, assessment TEXT, PRIMARY KEY (topic, level))"""
        )
        c.execute(
            """CREATE TABLE IF NOT EXISTS user_answers
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, topic TEXT, level TEXT, answers TEXT, score REAL)"""
        )
        conn.commit()


def store_content(topic, lesson, content):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute(
            "INSERT OR REPLACE INTO content (topic, lesson, content) VALUES (?, ?, ?)",
            (topic, lesson, content),
        )
        conn.commit()


def retrieve_content(topic, lesson):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute(
            "SELECT content FROM content WHERE topic = ? AND lesson = ?",
            (topic, lesson),
        )
        row = c.fetchone()
        if row:
            return row[0]
        return None


def store_problems(topic, level, problems):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute(
            "INSERT OR REPLACE INTO problems (topic, level, problems) VALUES (?, ?, ?)",
            (topic, level, problems),
        )
        conn.commit()


def retrieve_problems(topic, level):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute(
            "SELECT problems FROM problems WHERE topic = ? AND level = ?",
            (topic, level),
        )
        row = c.fetchone()
        if row:
            return row[0]
        return None


def store_assessment(topic, level, assessment):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute(
            "INSERT OR REPLACE INTO assessments (topic, level, assessment) VALUES (?, ?, ?)",
            (topic, level, assessment),
        )
        conn.commit()


def store_user_answers(topic, level, answers, score):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute(
            """
            INSERT OR REPLACE INTO user_answers (topic, level, answers, score)
            VALUES (?, ?, ?, ?)
            """,
            (topic, level, json.dumps(answers), score),
        )
        conn.commit()


def retrieve_assessment(topic, level):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute(
            "SELECT assessment FROM assessments WHERE topic = ? AND level = ?",
            (topic, level),
        )
        row = c.fetchone()
        if row:
            return row[0]
        return None


def generate_dynamic_content_groq(query, model_name=None, temperature=0.5):
    client = Groq()
    stream = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "As a math tutor, your task is to deliver clear, detailed, and comprehensive explanations of requested topics without the need for greetings. Your explanations should include examples and analogies to enhance understanding. Please ensure that your responses thoroughly explain the given topic and provide JSON response only when specifically requested. When providing a JSON response, remember to use two backward slashes in place of any single backward slashes present in the JSON to ensure correct display when rendered in the UI using streamlit. Avoid using the dollar symbol in your response unless absolutely necessary. If necessary, then use a single backslash before the dollar symbol unless it's a latex equation. Only provide a JSON response when asked to do so or if the JSON response format is specified.",
            },
            {"role": "user", "content": query},
        ],
        # model=model_name or "Llama-3.1-8b-Instant",
        model=model_name or "llama-3.2-90b-text-preview",
        temperature=temperature,
        top_p=1,
        stream=True,
    )

    response_text = ""
    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            response_text += content

    return response_text


def generate_dynamic_content_github(query, model_name=None, temperature=0.5):
    # Set your GitHub token and endpoint
    token = GITHUB_TOKEN
    endpoint = "https://models.inference.ai.azure.com"
    model_name = model_name or "gpt-4o-mini"

    # Initialize the OpenAI client
    client = OpenAI(
        base_url=endpoint,
        api_key=token,
    )

    # Create the chat request with streaming enabled
    stream = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "As a math tutor, your goal is to deliver thorough and comprehensive explanations of requested topics without the need for greetings. Your explanations should be clear, detailed, and inclusive of examples and analogies to enhance understanding. Please ensure that your responses aim to thoroughly explain the given topic and provide JSON response only when specifically requested. When providing a JSON response, remember to use two backward slashes in place of any single backward slashes present in the JSON to ensure correct display when rendered in the UI using streamlit. Avoid using the dollar symbol in your response unless absolutely necessary. If necessary, then use a single backslash before the dollar symbol unless it's a latex equation. Only provide a JSON response when asked to do so or if the JSON response format is specified.",
            },
            {"role": "user", "content": query},
        ],
        model=model_name,
        temperature=temperature,
        max_tokens=1024,
        top_p=1,
        stream=True,
    )

    # Collect the response as it streams
    response_text = ""
    for update in stream:
        if update.choices[0].delta.content:
            response_text += update.choices[0].delta.content

    return response_text


def generate_dynamic_content(
    query, model_type="groq", model_name=None, temperature=0.7
):
    if model_type == "groq":
        return generate_dynamic_content_groq(query, model_name, temperature)
    elif model_type == "github":
        return generate_dynamic_content_github(query, model_name, temperature)


def extract_json_from_response(response_text):
    """Extract the first valid JSON object from a given text."""
    brace_count = 0
    json_str = ""
    json_started = False

    for char in response_text:
        if char == "{":
            brace_count += 1
            json_started = True

        if json_started:
            json_str += char

        if char == "}":
            brace_count -= 1

        if json_started and brace_count == 0:
            break

    if brace_count == 0 and json_started:
        try:
            return json.loads(json_str)
        except (ValueError, json.JSONDecodeError) as e:
            # Print error for debugging
            print(f"Error decoding JSON: {e}")
            print(f"Problematic JSON string: {json_str}")
            st.error(
                "There was an error decoding the JSON response. Please generate again."
            )
            st.text(f"Error: {e}")
            st.text(f"JSON string: {json_str}")
    else:
        print("JSON brace count mismatch or JSON not started properly.")
        st.error("JSON brace count mismatch or JSON not started properly.")
        st.text(f"Response text: {response_text}")
        return None


create_db()
