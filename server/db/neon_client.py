import os
import asyncpg

async def get_db_connection():
    return await asyncpg.connect(os.getenv("NEON_DATABASE_URL"))

async def save_chat_history(session_id: str, role: str, content: str):
    conn = await get_db_connection()
    try:
        await conn.execute(
            "INSERT INTO history (session_id, role, content) VALUES ($1, $2, $3)",
            session_id, role, content,
        )
    finally:
        await conn.close()
