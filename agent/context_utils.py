
import sys
import asyncio
from  .db.db_model import insert,search

def add_context(data: str, session_id: str):
    value = insert({"session_id": session_id, **data})
    return value

async def get_context(session_id):
    return search(session_id)
