# SocraticDialogueAI

An AI-powered Socratic tutor that never gives answers directly. Instead it asks probing questions to guide you toward discovering answers yourself. Powered by a multi-model debate between GPT-4o, Claude, and Gemini.

**Live app:** https://socratic-dialogue-ai.vercel.app

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| LLM APIs | OpenAI GPT-4o, Anthropic Claude (claude-sonnet-4-6), Google Gemini (gemini-2.5-flash-lite) |
| NLP Preprocessing | spaCy (`en_core_web_md`) |
| Frontend | React, Vite |
| Deployment | Render (backend), Vercel (frontend) |

---

## How It Works

Each message triggers a **multi-agent debate** across three models before a response is shown:

1. User sends a message from the frontend along with the full conversation history.
2. spaCy lemmatizes and lowercases user input before it reaches any LLM.
3. GPT-4o, Claude, and Gemini are called **in parallel**. Each independently proposes a Socratic question.
4. GPT-4o **synthesizes** the best elements of all three proposals into one final response.
5. The synthesized question is returned to the frontend.
6. Each assistant message shows a **"Multi-agent debate"** toggle that reveals what each model proposed.

If any individual model fails (rate limit, bad key, etc.), the debate continues with the remaining models. If all three fail, it falls back to a direct GPT-4o call.

The backend is fully stateless, no server-side session storage.

---

## Local Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- API keys for OpenAI, Anthropic, and Google AI

### 1. Clone the repo

```bash
git clone https://github.com/SahusBhandary/SocraticDialogueAI.git
cd SocraticDialogueAI
```

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the `backend/` directory:

```
open_api_key=your_openai_api_key_here
anthropic_api_key=your_anthropic_api_key_here
gemini_api_key=your_google_api_key_here
```

Start the server:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

### 3. Frontend

```bash
cd frontend
npm install
```

Create a `.env` file in the `frontend/` directory:

```
VITE_API_URL=http://localhost:8000
```

Start the dev server:

```bash
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `POST` | `/chat` | Run the multi-agent debate and return a synthesized Socratic response |

### `POST /chat`

**Request body:**
```json
{
  "message": "What is gravity?",
  "history": [
    { "role": "assistant", "content": "Hi! I am your Socratic tutor..." }
  ]
}
```

**Response:**
```json
{
  "message": "What do you think causes objects to fall toward the ground?",
  "debate": {
    "gpt": "What evidence would you need to convince yourself that gravity exists?",
    "claude": "If gravity disappeared, what do you think would happen to the Moon?",
    "gemini": "What do you notice about how different objects fall when dropped from the same height?"
  }
}
```

---

## Deployment

### Backend (Render)

1. Create a new **Web Service** on [render.com](https://render.com) pointing to the `backend/` directory.
2. Set the following:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. Add environment variables:
   - `open_api_key` — OpenAI API key
   - `anthropic_api_key` — Anthropic API key (from [console.anthropic.com](https://console.anthropic.com))
   - `gemini_api_key` — Google API key (from [aistudio.google.com](https://aistudio.google.com))

### Frontend (Vercel)

1. Import the repo on [vercel.com](https://vercel.com).
2. Set the **Root Directory** to `frontend`.
3. Add environment variable: `VITE_API_URL` = your Render backend URL (no trailing slash).
