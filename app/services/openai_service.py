# app/services/openai_service.py
import os
from openai import OpenAI
import time
import asyncio
from dotenv import load_dotenv # <--- ADD THIS

load_dotenv() # <--- AND THIS

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

def get_or_create_thread(session_id: str, threads_state: dict) -> str:
    """Gets an existing thread ID for a session or creates a new one."""
    if session_id in threads_state:
        return threads_state[session_id]
    
    try:
        thread = client.beta.threads.create()
        threads_state[session_id] = thread.id
        print(f"Created new thread {thread.id} for session {session_id}")
        return thread.id
    except Exception as e:
        print(f"Error creating thread: {e}")
        raise

async def process_user_message(thread_id: str, user_message: str, system_prompt: str):
    """Adds a message, creates a run, and returns the run object."""
    if not ASSISTANT_ID:
        raise ValueError("ASSISTANT_ID is not configured in .env file.")

    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_message
    )

    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=ASSISTANT_ID,
        instructions=system_prompt
    )
    return run

async def await_run_completion(thread_id: str, run_id: str):
    """Waits for a run to complete or require action."""
    while True:
        await asyncio.sleep(1) # Non-blocking sleep for async
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        if run.status in ["completed", "requires_action", "failed", "cancelled"]:
            return run

def submit_tool_outputs(thread_id: str, run_id: str, tool_outputs: list):
    """Submits tool call results back to the Assistant."""
    try:
        run = client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread_id,
            run_id=run_id,
            tool_outputs=tool_outputs
        )
        return run
    except Exception as e:
        print(f"Error submitting tool outputs: {e}")
        raise

def get_latest_assistant_response(thread_id: str) -> str:
    """Retrieves the most recent message from the assistant in a thread."""
    try:
        messages = client.beta.threads.messages.list(thread_id=thread_id, order="desc", limit=1)
        if messages.data and messages.data[0].role == "assistant":
            response_text = ""
            for content_block in messages.data[0].content:
                if content_block.type == 'text':
                    response_text += content_block.text.value
            return response_text.strip()
        return "Assistant did not provide a text response."
    except Exception as e:
        print(f"Error retrieving assistant response: {e}")
        return "An error occurred while fetching the response."