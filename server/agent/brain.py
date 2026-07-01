import os
from typing import AsyncGenerator
from google import genai

from rag.qdrant_client import search_financial_docs
from db.neon_client import save_chat_history

# Initialize the Gemini client safely
try:
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
except ValueError:
    client = None  # Prevents crash on boot if the user hasn't added their key yet

async def process_query(session_id: str, transcript: str) -> AsyncGenerator[dict, None]:
    # 1. Always retrieve contextual RAG documents using Hybrid Search
    context = await search_financial_docs(transcript)
    
    # 2. Build the system prompt
    context_text = "\n\n".join([f"Source: {doc['source']}\nContent: {doc['content']}" for doc in context])
    system_instruction = (
        "You are a helpful, professional digital wealth advisor. "
        "Answer the user's questions based ONLY on the following context. "
        "Keep your answers extremely concise (1-2 sentences) so that the Text-to-Speech audio stays low latency.\n\n"
        f"CONTEXT:\n{context_text}"
    )

    # 3. Handle specific intent for our demo widget (optional UI demonstration)
    if "FD" in transcript.upper():
        yield {"type": "widget", "widget": "FDRateWidget", "data": {"rate": 7.1}}
    
    # 4. Stream the Gemini LLM response
    if not client:
        yield {"type": "text", "content": "The AI is currently offline. Please set GOOGLE_API_KEY."}
        return

    response = await client.aio.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents=transcript,
        config=genai.types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.3,
        )
    )

    async for chunk in response:
        if chunk.text:
            yield {"type": "text", "content": chunk.text}
