import asyncio
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI
import anthropic
from google import genai as google_genai
import spacy
from pydantic import BaseModel

load_dotenv()

openai_client = AsyncOpenAI(api_key=os.environ.get("open_api_key"))
anthropic_client = anthropic.AsyncAnthropic(api_key=os.environ.get("anthropic_api_key"))
gemini_client = google_genai.Client(api_key=os.environ.get("gemini_api_key"))

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

SYSTEM_PROMPT = "You are a Socratic tutor. Never give answers directly. Instead, ask probing questions that guide the user to discover the answer themselves."

DEBATE_PROMPT = "You are part of a multi-agent panel crafting Socratic questions. Given the student's question and conversation history, propose exactly one Socratic question that challenges their assumptions without giving the answer away. Respond with ONLY the question."

SYNTHESIS_PROMPT = "Three AI models proposed Socratic questions for a student. Synthesize the best elements of all three into one powerful Socratic question. Respond with ONLY the final question, no explanation."

class ChatInput(BaseModel):
    message: str
    history: list[dict] = []

def build_openai_context(history: list[dict], message: str, system: str) -> list[dict]:
    context = [{"role": "system", "content": system}]
    for m in history:
        role = m.get("role")
        content = m.get("content", "")
        if role == "user":
            context.append({"role": "user", "content": pre_process_text(content)})
        elif role == "assistant":
            context.append({"role": "assistant", "content": content})
    context.append({"role": "user", "content": pre_process_text(message)})
    return context

def build_gemini_contents(history: list[dict], message: str) -> list[dict]:
    contents = []
    for m in history:
        role = m.get("role")
        content = m.get("content", "")
        if role == "user":
            contents.append({"role": "user", "parts": [{"text": pre_process_text(content)}]})
        elif role == "assistant":
            contents.append({"role": "model", "parts": [{"text": content}]})
    contents.append({"role": "user", "parts": [{"text": pre_process_text(message)}]})
    return contents

async def get_gpt_perspective(history: list[dict], message: str) -> str | None:
    try:
        context = build_openai_context(history, message, DEBATE_PROMPT)
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=context,
            max_tokens=256,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"GPT-4o debate error: {e}")
        return None

async def get_claude_perspective(history: list[dict], message: str) -> str | None:
    try:
        messages = []
        for m in history:
            role = m.get("role")
            content = m.get("content", "")
            if role == "user":
                messages.append({"role": "user", "content": pre_process_text(content)})
            elif role == "assistant":
                messages.append({"role": "assistant", "content": content})
        messages.append({"role": "user", "content": pre_process_text(message)})

        response = await anthropic_client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=256,
            system=DEBATE_PROMPT,
            messages=messages,
        )
        return response.content[0].text
    except Exception as e:
        print(f"Claude debate error: {e}")
        return None

async def get_gemini_perspective(history: list[dict], message: str) -> str | None:
    try:
        contents = build_gemini_contents(history, message)
        response = await gemini_client.aio.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=contents,
            config=google_genai.types.GenerateContentConfig(
                system_instruction=DEBATE_PROMPT,
                max_output_tokens=256,
            ),
        )
        return response.text
    except Exception as e:
        print(f"Gemini debate error: {e}")
        return None

async def synthesize(gpt: str | None, claude: str | None, gemini: str | None, history: list[dict], message: str) -> str:
    perspectives = {k: v for k, v in {"GPT-4o": gpt, "Claude": claude, "Gemini": gemini}.items() if v}

    if not perspectives:
        # All models failed — fall back to a direct GPT-4o call
        context = build_openai_context(history, message, SYSTEM_PROMPT)
        response = await openai_client.chat.completions.create(model="gpt-4o", messages=context)
        return response.choices[0].message.content

    if len(perspectives) == 1:
        return next(iter(perspectives.values()))

    proposals = "\n".join(f'{name}: "{q}"' for name, q in perspectives.items())
    synthesis_context = [
        {"role": "system", "content": SYNTHESIS_PROMPT},
        {"role": "user", "content": f"Student question: \"{message}\"\n\nProposals:\n{proposals}"},
    ]
    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=synthesis_context,
        max_tokens=256,
    )
    return response.choices[0].message.content

@app.get("/")
async def root():
    return {"status": "ok"}

@app.post("/chat")
async def chat(input: ChatInput):
    try:
        gpt, claude, gemini = await asyncio.gather(
            get_gpt_perspective(input.history, input.message),
            get_claude_perspective(input.history, input.message),
            get_gemini_perspective(input.history, input.message),
        )

        final = await synthesize(gpt, claude, gemini, input.history, input.message)

        return {
            "message": final,
            "debate": {"gpt": gpt, "claude": claude, "gemini": gemini},
        }
    except Exception as e:
        print(f"Chat error: {e}")
        return {"error": str(e)}
