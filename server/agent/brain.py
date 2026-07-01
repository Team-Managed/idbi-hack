from typing import AsyncGenerator
from rag.qdrant_client import search_financial_docs
from db.neon_client import save_chat_history

async def process_query(session_id: str, transcript: str) -> AsyncGenerator[dict, None]:
    if "FD" in transcript:
        context = await search_financial_docs(transcript)
        source = context[0]["source"] if context else "our records"

        yield {"type": "widget", "widget": "FDRateWidget", "data": {"rate": 7.1}}
        yield {"type": "text", "content": f"The current FD rate is 7.1%, based on {source}."}
    else:
        yield {"type": "text", "content": "Let me look into that for you."}
