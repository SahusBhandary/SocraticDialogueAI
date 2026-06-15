from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
import spacy
from pydantic import BaseModel
from collections import defaultdict

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
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

SYSTEM_PROMPT = {"role": "system", "content": "You are a Socratic tutor. Never give answers directly. Instead, ask probing questions that guide the user to discover the answer themselves."}

def new_session():
    return [SYSTEM_PROMPT]

histories = defaultdict(new_session)

class ChatInput(BaseModel):
    message: str
    session_id: str

@app.get("/history/{session_id}")
async def get_history(session_id: str):
    messages = [m for m in histories[session_id] if m["role"] != "system"]
    return {"messages": messages}

@app.post("/chat")
async def chat(input: ChatInput):
    try:
        histories[input.session_id].append({"role": "user", "content": input.message})

        ai_context = [
            {"role": m["role"], "content": pre_process_text(m["content"]) if m["role"] == "user" else m["content"]}
            for m in histories[input.session_id]
        ]

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=ai_context,
        )

        ai_response = response.choices[0].message.content
        histories[input.session_id].append({"role": "assistant", "content": ai_response})

        return {"message": ai_response}
    except OpenAIError as e:
        print(f"OpenAI API Error: {e}")
        return {"error": str(e)}
