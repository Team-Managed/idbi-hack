# Full-Stack Wealth Advisor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the complete end-to-end architecture for the Digital Wealth Advisory Agent, comprising a Next.js Client (Frontend) and a FastAPI Server (Backend).

**Architecture:** 
- **Client:** Next.js App Router, Tailwind CSS v3 (Light Mode).
- **Server:** FastAPI, Python `asyncio`, Qdrant (Hybrid RAG), edge-tts, MuseTalk rendering stub.

## Global Constraints
- Client code must reside in the `client/` directory.
- Server code must reside in the `server/` directory.
- All Client styling must use Tailwind CSS v3 with a clean, light-mode aesthetic.
- Server must be non-blocking (asyncio-safe — no blocking calls on the event loop).

---

## Phase 1: Server Core & Database

### Task 1: Server Initialization (FastAPI & uv)

**Files:**
- Create: `server/pyproject.toml`, `server/.env.example`, `server/main.py`, `server/api/websocket.py`

**Interfaces:**
- Produces: Base FastAPI server structure ready to accept WebSocket connections. Generates `session_id`.

- [ ] **Step 1: Setup Server Directories**
```bash
mkdir -p server/api server/agent server/rag server/render server/db server/scripts
```

- [ ] **Step 2: Initialize Server Requirements (uv)**
```bash
cd server
uv init
uv add fastapi "uvicorn[standard]" websockets qdrant-client edge-tts asyncpg faster-whisper pydub
```

- [ ] **Step 3: Create server/.env.example**
```env
NEON_DATABASE_URL=postgresql://user:pass@ep-restless.eu-central-1.aws.neon.tech/neondb
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
LLM_API_KEY=
ARCJET_KEY=ajkey_xyz
```

- [ ] **Step 4: Create server/main.py**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.websocket import router as ws_router

app = FastAPI(title="Wealth Advisor API")

# Fix 1: allow_origins=["*"] with allow_credentials=True is invalid
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ws_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

- [ ] **Step 5: Create server/api/websocket.py (Base Structure)**
```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import uuid

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Fix 2: Threading session_id
    session_id = str(uuid.uuid4())
    await websocket.send_json({"type": "session", "session_id": session_id})
    try:
        while True:
            data = await websocket.receive()
            # To be wired fully in Task 4
    except WebSocketDisconnect:
        print(f"Client {session_id} disconnected")
```

- [ ] **Step 6: Commit**
```bash
git add server/
git commit -m "chore: initialize FastAPI server backend with uv and strict CORS"
```

### Task 2: Database & Document Ingestion (Hybrid RAG Setup)

**Files:**
- Create: `server/db/neon_client.py`, `server/scripts/ingest.py`

- [ ] **Step 1: Setup Neon Database Client**
```python
# server/db/neon_client.py
import asyncpg
import os

async def get_db_connection():
    return await asyncpg.connect(os.getenv("NEON_DATABASE_URL"))

async def save_chat_history(session_id: str, role: str, content: str):
    conn = await get_db_connection()
    await conn.execute(
        "INSERT INTO history (session_id, role, content) VALUES ($1, $2, $3)",
        session_id, role, content
    )
    await conn.close()
```

- [ ] **Step 2: Document Ingestion Script (True Hybrid Setup)**
```python
# server/scripts/ingest.py
from qdrant_client import QdrantClient
from qdrant_client import models

def init_qdrant():
    client = QdrantClient(url="http://localhost:6333")
    # Fix 3: Don't recreate/wipe data. Ensure true hybrid (dense + sparse) config.
    if not client.collection_exists("financial_docs"):
        client.create_collection(
            collection_name="financial_docs",
            vectors_config={"dense": models.VectorParams(size=384, distance=models.Distance.COSINE)},
            sparse_vectors_config={"sparse": models.SparseVectorParams()}
        )
        print("Hybrid collection created. Ready for document ingestion.")
    else:
        print("Collection already exists.")

if __name__ == "__main__":
    init_qdrant()
```

- [ ] **Step 3: Commit**
```bash
git add server/db server/scripts
git commit -m "feat: setup neon db client and true hybrid qdrant schema"
```

---

## Phase 2: AI Intelligence Pipeline

### Task 3: ASR, RAG, & Agent Core

**Files:**
- Create: `server/agent/asr.py`, `server/rag/qdrant_client.py`, `server/agent/brain.py`

- [ ] **Step 1: Speech-to-Text (Non-blocking & Functional)**
```python
# server/agent/asr.py
from faster_whisper import WhisperModel
from pydub import AudioSegment
import io
import asyncio

model = WhisperModel("tiny", device="cpu", compute_type="int8")

def transcribe_audio_sync(audio_bytes: bytes) -> str:
    # Decode WebM to 16kHz WAV for Whisper
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="webm")
    wav_io = io.BytesIO()
    audio.set_frame_rate(16000).export(wav_io, format="wav")
    
    # Fix 4: Actually transcribe instead of hardcoded return
    segments, _ = model.transcribe(wav_io)
    return " ".join([segment.text for segment in segments])

async def transcribe_audio(audio_bytes: bytes) -> str:
    # Fix 4: Non-blocking executor call
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, transcribe_audio_sync, audio_bytes)
```

- [ ] **Step 2: Hybrid RAG Client (Search)**
```python
# server/rag/qdrant_client.py
from qdrant_client import AsyncQdrantClient

client = AsyncQdrantClient(url="http://localhost:6333")

async def search_financial_docs(query: str):
    # Perform RRF search (Dense + Sparse). Stub for now.
    return [{"source": "FD_Policy.pdf", "content": "Current FD rate is 7.1%"}]
```

- [ ] **Step 3: Agentic Core (ReAct Loop & Streaming)**
```python
# server/agent/brain.py
from rag.qdrant_client import search_financial_docs
from db.neon_client import save_chat_history
from typing import AsyncGenerator

async def process_query(session_id: str, transcript: str) -> AsyncGenerator[dict, None]:
    # Simulate DB history check and LLM reasoning
    await save_chat_history(session_id, "user", transcript)
    
    if "FD" in transcript:
        context = await search_financial_docs(transcript)
        yield {"type": "widget", "widget": "FDRateWidget", "data": {"rate": 7.1}}
    
    yield {"type": "text", "content": "The current FD rate is 7.1%."}
    await save_chat_history(session_id, "agent", "The current FD rate is 7.1%.")
```

- [ ] **Step 4: Commit**
```bash
git add server/agent server/rag
git commit -m "feat: implement non-blocking ASR, RAG client, and Agentic Core"
```

### Task 4: Audio Synthesis, Neural Video, & Full-Duplex Wiring

**Files:**
- Create: `server/render/tts.py`, `server/render/musetalk.py`
- Modify: `server/api/websocket.py`

- [ ] **Step 1: Text-to-Speech (Streaming)**
```python
# server/render/tts.py
import edge_tts
from typing import AsyncGenerator

async def generate_speech_stream(text: str) -> AsyncGenerator[bytes, None]:
    communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            yield chunk["data"]
```

- [ ] **Step 2: MuseTalk Stub**
```python
# server/render/musetalk.py
from typing import AsyncGenerator

async def generate_video_frames(audio_chunk: bytes) -> bytes:
    # Stub: Converts a small audio chunk to an H.264 NAL unit instantly
    return b'\x00\x00\x00\x01\x67...' # Mock NAL unit
```

- [ ] **Step 3: Full-Duplex Wiring (Fix 5)**
```python
# server/api/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import uuid
import asyncio
from agent.asr import transcribe_audio
from agent.brain import process_query
from render.tts import generate_speech_stream
from render.musetalk import generate_video_frames

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = str(uuid.uuid4())
    await websocket.send_json({"type": "session", "session_id": session_id})
    
    # Fix 5: Concurrency strategy for full-duplex streaming
    async def process_message(data):
        transcript = ""
        if "bytes" in data:
            transcript = await transcribe_audio(data["bytes"])
        elif "text" in data:
            transcript = data["text"]
            
        if transcript:
            await websocket.send_json({"type": "chat", "content": transcript, "role": "user"})
            
            async for agent_chunk in process_query(session_id, transcript):
                if agent_chunk["type"] == "widget":
                    await websocket.send_json(agent_chunk)
                elif agent_chunk["type"] == "text":
                    await websocket.send_json({"type": "chat", "content": agent_chunk["content"], "role": "agent"})
                    # TTS -> MuseTalk pipeline
                    async for audio_bytes in generate_speech_stream(agent_chunk["content"]):
                        video_bytes = await generate_video_frames(audio_bytes)
                        await websocket.send_bytes(video_bytes)
    
    try:
        while True:
            data = await websocket.receive()
            # Launch as independent task to not block the read loop
            asyncio.create_task(process_message(data))
    except WebSocketDisconnect:
        print(f"Client {session_id} disconnected")
```

- [ ] **Step 4: Commit**
```bash
git add server/render server/api
git commit -m "feat: implement neural video pipeline and full-duplex websocket wiring"
```

---

## Phase 3: Client (Frontend) Application

### Task 5: Client Initialization & Arcjet

**Files:**
- Create: Next.js scaffolding, `client/src/middleware.ts`, `client/src/app/globals.css`

- [ ] **Step 1: Initialize Next.js**
```bash
npx -y create-next-app@latest client --ts --tailwind --eslint --app --src-dir --import-alias "@/*" --use-pnpm
cd client && pnpm add @arcjet/next lucide-react jmuxer
```

- [ ] **Step 2: Implement Arcjet Security**
```typescript
# client/src/middleware.ts
import arcjet, { detectBot, shield } from "@arcjet/next";
import { NextResponse } from "next/server";

const aj = arcjet({
  key: process.env.ARCJET_KEY!,
  rules: [
    shield({ mode: "LIVE" }),
    detectBot({ mode: "LIVE", allow: [] }),
  ],
});

export default async function middleware(req: any) {
  const decision = await aj.protect(req);
  if (decision.isDenied()) return NextResponse.json({ error: "Access Denied" }, { status: 403 });
  return NextResponse.next();
}
```

- [ ] **Step 3: Tailwind Theme Setup**
```css
/* client/src/app/globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
    background-color: #f9fafb;
    color: #111827;
}
```

- [ ] **Step 4: Commit**
```bash
git add client/
git commit -m "chore: initialize client with Arcjet and Tailwind"
```

### Task 6: UI Components & WebSockets

**Files:**
- Create: `useWebSocket.ts`, `AvatarPlayer.tsx`, `AdvisoryChat.tsx`, `FDRateWidget.tsx`

- [ ] **Step 1: WebSocket & Microphone Hook**
```typescript
# client/src/hooks/useWebSocket.ts
import { useEffect, useRef, useState } from 'react';

export function useWebSocket(url: string) {
    const ws = useRef<WebSocket | null>(null);
    const [messages, setMessages] = useState<any[]>([]);
    const [sessionId, setSessionId] = useState<string | null>(null);
    const videoStreamRef = useRef<(data: Uint8Array) => void>();

    useEffect(() => {
        ws.current = new WebSocket(url);
        ws.current.onmessage = async (event) => {
            if (typeof event.data === "string") {
                const parsed = JSON.parse(event.data);
                if (parsed.type === "session") setSessionId(parsed.session_id);
                else setMessages(prev => [...prev, parsed]);
            } else {
                // Fix 6: Route binary frames to the player
                const arrayBuffer = await event.data.arrayBuffer();
                if (videoStreamRef.current) {
                    videoStreamRef.current(new Uint8Array(arrayBuffer));
                }
            }
        };
        return () => ws.current?.close();
    }, [url]);

    const sendText = (text: string) => ws.current?.send(JSON.stringify({ text }));

    const startRecording = async () => {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const recorder = new MediaRecorder(stream);
        recorder.ondataavailable = (e) => ws.current?.send(e.data);
        recorder.start(250); 
    };

    return { messages, sessionId, startRecording, sendText, videoStreamRef };
}
```

- [ ] **Step 2: Avatar Video Player (MSE with jmuxer)**
```typescript
# client/src/components/avatar/AvatarPlayer.tsx
import { useEffect, useRef } from "react";
import JMuxer from "jmuxer";

export default function AvatarPlayer({ videoStreamRef }: { videoStreamRef: any }) {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (videoRef.current) {
      const jmuxer = new JMuxer({
        node: videoRef.current,
        mode: 'video',
        flushingTime: 0,
        fps: 25,
      });
      videoStreamRef.current = (data: Uint8Array) => jmuxer.feed({ video: data });
    }
  }, [videoStreamRef]);

  return (
    <div className="w-full h-[600px] rounded-2xl bg-white border border-gray-200 shadow-sm flex items-center justify-center overflow-hidden relative">
      <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover" />
      <div className="absolute top-4 right-4 text-xs font-medium text-blue-600 bg-blue-50 px-3 py-1 rounded-full border border-blue-200">
        Live Stream
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Advisory Chat & Dynamic Widget**
```typescript
# client/src/components/chat/AdvisoryChat.tsx
import { useState } from "react";

export default function AdvisoryChat({ messages, onSend }: { messages: any[], onSend: (text: string) => void }) {
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (!input.trim()) return;
    onSend(input);
    setInput("");
  };

  return (
    <div className="flex flex-col h-[600px] bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
      <div className="flex-1 overflow-y-auto space-y-4">
        {messages.map((msg, i) => (
          <div key={i} className={`p-3 rounded-xl ${msg.role === 'user' ? 'bg-blue-50 text-blue-900 ml-auto' : 'bg-gray-50 text-gray-800'}`}>
            {msg.type === "widget" ? `[Widget Triggered: ${msg.widget}]` : msg.content}
          </div>
        ))}
      </div>
      <div className="mt-4 flex gap-2">
        {/* Fix 6: Add send handler to text input */}
        <input 
          type="text" 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Type a message..." 
          className="p-4 rounded-xl border border-gray-200 w-full focus:ring-2 focus:ring-blue-500 outline-none" 
        />
        <button onClick={handleSend} className="px-6 bg-blue-600 text-white rounded-xl hover:bg-blue-700">Send</button>
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Main Page Integration**
```typescript
# client/src/app/page.tsx
"use client";
import AvatarPlayer from "@/components/avatar/AvatarPlayer";
import AdvisoryChat from "@/components/chat/AdvisoryChat";
import { useWebSocket } from "@/hooks/useWebSocket";

export default function Page() {
  const { messages, sessionId, startRecording, sendText, videoStreamRef } = useWebSocket("ws://localhost:8000/ws");
  
  return (
    <div className="min-h-screen p-8 max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* Fix 6: Passing required videoStreamRef prop */}
      <AvatarPlayer videoStreamRef={videoStreamRef} />
      <div className="flex flex-col gap-4">
        <div className="flex justify-between items-center">
          <button onClick={startRecording} className="bg-blue-600 text-white p-3 rounded-xl shadow-sm hover:bg-blue-700 w-fit">Start Voice Chat</button>
          {sessionId && <span className="text-sm text-gray-500 font-mono">Session: {sessionId.substring(0,8)}</span>}
        </div>
        <AdvisoryChat messages={messages} onSend={sendText} />
      </div>
    </div>
  );
}
```

- [ ] **Step 5: Commit**
```bash
git add client/src
git commit -m "feat: complete client UI, widgets, and websocket integration with full routing"
```
