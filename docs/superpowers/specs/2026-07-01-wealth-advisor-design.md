# Full-Stack Digital Wealth Advisory Agent - Design Spec

## Overview
A comprehensive full-stack application for the IDBI Hackathon, functioning as a real-time Digital Wealth Advisory Agent. The system is split into two distinct tiers:
1. **Client (Frontend):** A Next.js web application providing a premium user interface.
2. **Server (Backend):** A FastAPI Python application handling AI orchestration, hybrid RAG, and neural video generation.

## Entire Architecture & Tech Stack

### Client (Frontend) Tier
- **Framework:** Next.js (App Router) with TypeScript.
- **Package Manager:** `pnpm`
- **Styling:** Tailwind CSS v3 (Light Mode focused).
- **Icons:** `lucide-react`
- **Responsibilities:**
  - Premium light-mode UI with clean, minimalist aesthetics (`bg-white`, `shadow-sm`, `text-blue-600`).
  - Capture user audio/text input.
  - Play back the live H.264 video stream via an HTML5 `<video>` element (`AvatarPlayer`).
  - Display real-time chat transcripts and dynamic financial widgets (e.g., FD Rates, Mutual Funds).

### Server (Backend) Tier
- **Framework:** FastAPI (Python 3.10+) running on `uvicorn`.
- **Database / Vector Store:** Neon PostgreSQL & Qdrant.
- **Security:** Arcjet (Wasm-based security for rate limiting and prompt injection defense).
- **AI Models & Pipeline:**
  - **ASR:** Whisper (converts incoming audio to text).
  - **Agentic Core:** Gemini/Llama via ReAct loop (orchestrates logic).
  - **Hybrid RAG:** Dense (MiniLM) + Sparse (BM25) search with Reciprocal Rank Fusion (RRF) on Qdrant.
  - **TTS:** `edge-tts` (converts agent text response to audio).
  - **Neural Rendering:** MuseTalk (generates lip-synced H.264 video frames from TTS audio and base avatar image).
- **Responsibilities:**
  - Expose a WebSocket endpoint (`api/websocket.py`) for bi-directional streaming.
  - Execute the heavy AI inference pipeline.
  - Stream continuous H.264 video chunks back to the client.

## Data Flow (End-to-End)
1. **User Input:** User speaks or types into the Next.js Client.
2. **Transmission:** Client sends audio/text chunks to the FastAPI Server via WebSocket.
3. **Transcription (ASR):** Server uses Whisper to transcribe audio.
4. **Reasoning (Agent):** Agentic LLM analyzes the query and issues a tool call to the Hybrid RAG (Qdrant) if financial context is needed.
5. **Synthesis (TTS):** LLM response text is converted to speech via `edge-tts`.
6. **Rendering (Video):** TTS audio is fed into the MuseTalk stub/engine to generate H.264 frames.
7. **Streaming:** Server pushes H.264 video chunks and chat UI JSON metadata over the WebSocket.
8. **Display:** Client `<video>` element plays the stream; UI updates with chat bubbles and widgets.
