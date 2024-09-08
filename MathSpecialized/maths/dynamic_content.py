# dynamic_content.py
# import streamlit as st
from utils.mathutils import get_response_from_api
from dotenv import load_dotenv

def generate_dynamic_content_ollama(query):
    response = get_response_from_api(query)
    return response

load_dotenv()

## Example usage in personalized learning
# query = "Explain the concept of quadratic equations."
# explanation = generate_dynamic_content(query)
# st.write(explanation)


# dynamic_content.py

from groq import Groq


def generate_dynamic_content(query):
    client = Groq()
    stream = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful math tutor."},
            {"role": "user", "content": query},
        ],
        model="llama3-8b-8192",
        temperature=0.5,
        max_tokens=1024,
        top_p=1,
        stream=True,
    )

    response_text = ""
    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            response_text += content
            # yield content

    return response_text
