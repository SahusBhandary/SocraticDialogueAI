# SocraticDialogueAI

An AI-powered Socratic tutor that never gives answers directly. Instead it asks probing questions to guide you toward discovering answers yourself.

**Live app:** https://socratic-dialogue-ai.vercel.app

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, OpenAI GPT-4o |
| NLP Preprocessing | spaCy (`en_core_web_md`) |
| Frontend | React, Vite |
| Deployment | Render (backend), Vercel (frontend) |

---

## How It Works

1. User sends a message from the frontend.
2. The full conversation history is sent to the FastAPI backend with each request.
3. spaCy lemmatizes and lowercases user input before it reaches the LLM.
4. GPT-4o responds using a Socratic system prompt. It never answers directly.
5. The response is returned and displayed in the chat UI.

The backend is fully stateless, no server-side session storage.

---

## Local Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- An OpenAI API key

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
| `POST` | `/chat` | Send a message and receive a Socratic response |

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
  "message": "What do you think causes objects to fall toward the ground?"
}
```

---

## Deployment

### Backend (Render)

1. Create a new **Web Service** on [render.com](https://render.com) pointing to the `backend/` directory.
2. Set the following:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. Add environment variable: `open_api_key` = your OpenAI API key.

### Frontend (Vercel)

1. Import the repo on [vercel.com](https://vercel.com).
2. Set the **Root Directory** to `frontend`.
3. Add environment variable: `VITE_API_URL` = your Render backend URL (no trailing slash).
