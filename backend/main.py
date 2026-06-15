from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from openai import OpenAI
import spacy

load_dotenv()
client = OpenAI(api_key = os.environ.get("open_api_key"))

app = FastAPI()

# Text Pre-Processing Function
nlp = spacy.load("en_core_web_md")
def pre_process_text(text):
    doc = nlp(text)
    tokens = [token.lemma_.lower() for token in doc if not token.is_punct and not token.is_space]
    return " ".join(tokens)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Messages memory
messages = [
    {
        "role": "system",
        "content": "You are a Socratic tutor. Never give answers directly. Instead, ask probing questions that guide the user to discover the answer themselves.",
    }
]

@app.get("/ai")
async def ai_call(user_input: str = "Hello!"):
    try:
        processed_text = pre_process_text(user_input)
        # Append user message to messages memory
        messages.append({"role": "user", "content": processed_text})

        # Send full chat history to AI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )

        # Save AI Response
        ai_response = response.choices[0].message.content
        
        # Add AI response to messages memory
        messages.append({"role": "assistant", "content": ai_response})

        return ({"message": ai_response})
    except OpenAIError as e:
        print(f"Open AI API Error: {e}")
        return {"error": e}