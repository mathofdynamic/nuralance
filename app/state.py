# app/state.py

# In-memory storage for the demo. For production, use Redis or a database.
# Maps session_id to user-specific data like their DB path and system prompt.
USER_SESSIONS = {}

# In-memory storage for OpenAI thread IDs.
# Maps session_id to thread_id.
SESSION_THREADS = {}