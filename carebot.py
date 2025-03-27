import together
from typing import Final
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY: Final[str] = os.getenv('API_KEY')

client = together.Together(api_key=API_KEY)

# Function to generate quiz questions
def generate_question(age, topic):
    system_instruction = {
        "role": "system",
        "content": (
            f"You are Quizzy, an AI Quiz Master. Your task is to create engaging and age-appropriate quiz questions. "
            f"The user is {age} years old, and they want questions on the topic '{topic}'. "
            f"Provide a question, its correct answer, and a brief explanation. Format the response as: "
            f"Question: <question>\nAnswer: <answer>\nExplanation: <explanation>"
        )
    }

    completion = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        messages=[system_instruction],
        max_tokens=200,
        temperature=0.7,
        top_p=1.0)

    response = completion.choices[0].message.content
    return response

# Function to generate explanations
def generate_explanation(question):
    system_instruction = {
        "role": "system",
        "content": (
            f"You are Quizzy, an AI Quiz Master. Provide a detailed explanation for the following question: '{question}'. "
            f"Keep the explanation concise and easy to understand."
        )
    }

    completion = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        messages=[system_instruction],
        max_tokens=200,
        temperature=0.7,
        top_p=1.0)

    response = completion.choices[0].message.content
    return response