# AI Wealth Advisor

An advanced, real-time AI digital wealth advisory platform featuring a full-duplex conversational voice interface, low-latency text-to-speech, neural video generation (lip-sync), and hybrid RAG-augmented intelligence.

## 🏗️ Architecture & Tech Stack

This repository is a monorepo consisting of a robust backend for AI orchestration and a Next.js frontend.

### Backend (`/server`)
- **Framework:** FastAPI (Python 3.12)
- **Package Manager:** `uv`
- **Real-Time Pipeline:** Session-aware, thread-safe asynchronous WebSockets.
- **Agent Intelligence:** LangChain / custom ReAct-style LLM routing.
- **RAG Engine:** Qdrant Cloud (Reciprocal Rank Fusion hybrid search using `BAAI/bge-small-en-v1.5` dense embeddings and `bm25` sparse embeddings via `fastembed`).
- **Database:** Neon PostgreSQL (using `asyncpg` for chat history persistence).
- **Speech Pipeline:** 
  - **ASR:** `faster-whisper` for non-blocking local audio transcription.
  - **TTS:** `edge-tts` for real-time streaming audio generation.
  - **Video:** Neural lip-sync stub (`MuseTalk`) rendering H.264 binary frames dynamically.

### Frontend (`/client`)
- **Framework:** Next.js 15 (App Router)
- **Styling:** Tailwind CSS v3 (Light Mode UI)
- **Security:** Arcjet (Middleware-level bot protection & live shield)
- **Media Decoding:** `jmuxer` for raw H.264 WebSockets video parsing and rendering.
- **Audio Capture:** Standard `MediaRecorder` API sending chunked blobs to the server.

---

## 🚀 Getting Started

### 1. Prerequisites
- **Node.js** (v18+) and **pnpm**
- **Python 3.12** and **uv**
- FFMPEG installed on your system (required for `pydub` audio manipulation on the backend)
- API Keys for Qdrant Cloud, Neon DB, LLM Provider, and Arcjet.

### 2. Backend Setup
1. Navigate to the server directory:
   ```bash
   cd server
   ```
2. Create and populate your environment variables:
   ```bash
   cp .env.example .env
   ```
   *Make sure to fill in your NeonDB, Qdrant, and LLM credentials.*
3. Start the FastAPI server (uv will automatically sync the `3.12` environment and install dependencies):
   ```bash
   uv run uvicorn main:app --reload
   ```

### 4. LLM API (Server-side Agent)
1. Sign up for your preferred LLM provider (e.g., [OpenAI](https://platform.openai.com/api-keys) or [Anthropic](https://console.anthropic.com/)) or use Google AI Studio for Gemini.
2. Generate a secret API key.
3. Open **`server/.env`** and add it:
   ```env
   GOOGLE_API_KEY=sk-your_llm_api_key_here
   ```

### 3. Frontend Setup
1. Navigate to the client directory:
   ```bash
   cd client
   ```
2. Create your environment variables:
   ```bash
   echo "ARCJET_KEY=your_arcjet_key_here" > .env.local
   ```
3. Install dependencies and start the dev server:
   ```bash
   pnpm install
   pnpm dev
   ```

### 4. Running the App
Open [http://localhost:3000](http://localhost:3000) in your browser. 
- Click **Start Voice Chat** to grant microphone permissions and begin speaking to the advisor.
- Click **Stop** to dispatch your voice query.
- Use the **Chat Box** to seamlessly transition to text queries on the same connection.
- The `AvatarPlayer` will render the live video stream corresponding to the agent's TTS response.

---

## 🔧 Core Mechanics
- **Full-Duplex Async WebSockets:** The system doesn't rely on linear HTTP polling. Voice chunks, text queries, and system events stream bidirectionally via a single unified WebSocket connection (`/ws`).
- **Pipelined Orchestration:** The backend processes workloads via `asyncio.create_task`. Audio is transcribed, queried against the hybrid RAG, evaluated by the LLM, piped through TTS, and fed to the neural video generator concurrently without blocking the read socket.
- **Smart Turn Boundaries:** Voice interactions use an explicit `"end_of_turn"` semantic to perfectly delineate when the user is done speaking, ensuring transcription only happens on complete thought chunks.
- **Zero-Latency Buffering:** To appease neural video generator requirements without incurring massive latency, TTS outputs are buffered by *sentence chunks* (as yielded by the agent) rather than waiting for the entire LLM response to complete.
