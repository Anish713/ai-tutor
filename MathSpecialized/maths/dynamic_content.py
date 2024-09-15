import sqlite3
from openai import OpenAI
import streamlit as st
from groq import Groq
from utils.mathutils import get_response_from_api
import json
import os

DB_PATH = "generated_content.db"


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


def generate_dynamic_content_groq(query):
    client = Groq()
    stream = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a helpful math tutor. You have to respond like an actual human tutor while trying your best to clearly explain the given topic in detail. Use examples and analogy if necessary. For any mathematical equations present, you respond with it's respective latex code instead of direct mathematical equation since direct mathematical equations are not rendered properly in UI. When providing a JSON response, you must use two forward slashes in place of any single forward slashes present in the JSON to ensure correct display in the UI.",
            },
            {"role": "user", "content": query},
        ],
        # model="llama3-8b-8192",
        model="Llama-3.1-8b-Instant",
        # model="Llama-3.1-70b-Versatile",
        # model="gemma2-9b-it",
        # model="mixtral-8x7b-32768",
        temperature=0.5,
        top_p=1,
        stream=True,
    )

    response_text = ""
    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            response_text += content

    return response_text


def generate_dynamic_content_github(query):
    # Set your GitHub token and endpoint
    token = os.environ["GITHUB_TOKEN"]
    endpoint = "https://models.inference.ai.azure.com"
    # model_name = "gpt-4o-mini"
    model_name = "gpt-4o"

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
                "content": "You are a helpful math tutor. You have to respond like an actual human tutor while trying your best to clearly explain the given topic in detail. Use examples and analogy if necessary. Your given equations should be in structured way for rendering in user interface since direct mathematical equations are not rendered properly in UI. And for the same reason, whenever asked to give json response give two forward slash instead of single forward slashes whereever needed in your json response.",
                # "content": "Respond to the user as a real human tutor would, focusing on providing clear, detailed explanations.  For Equations: When explaining any mathematical concept that involves equations, respond using LaTeX code for better rendering in the UI. Use simple language, examples, and analogies when appropriate to help the user grasp the concepts. For JSON Requests: When providing a JSON response, must use two forward slashes (\\ \\) in place of any single forward slash(\\) in the JSON code to ensure correct display in the UI.",
            },
            {"role": "user", "content": query},
        ],
        model=model_name,
        temperature=0.5,
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


def generate_dynamic_content(query, model_type="groq"):
    if model_type == "groq":
        return generate_dynamic_content_groq(query)
    elif model_type == "github":
        return generate_dynamic_content_github(query)


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
