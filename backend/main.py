from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
import spacy
from pydantic import BaseModel

load_dotenv()
client = OpenAI(api_key=os.environ.get("open_api_key"))

app = FastAPI()

nlp = spacy.load("en_core_web_md")

def pre_process_text(text):
    doc = nlp(text)
    tokens = [token.lemma_.lower() for token in doc if not token.is_punct and not token.is_space]
    return " ".join(tokens)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

messages = [
    {"role": "system", "content": "You are a Socratic tutor. Never give answers directly. Instead, ask probing questions that guide the user to discover the answer themselves."}
]

class ChatInput(BaseModel):
    message: str

@app.get("/")
async def root():
    return {"status": "ok"}

@app.post("/chat")
async def chat(input: ChatInput):
    try:
        messages.append({"role": "user", "content": pre_process_text(input.message)})

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )

        ai_response = response.choices[0].message.content
        messages.append({"role": "assistant", "content": ai_response})

        return {"message": ai_response}
    except OpenAIError as e:
        print(f"OpenAI API Error: {e}")
        return {"error": str(e)}
