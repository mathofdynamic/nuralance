# app/routers/chatbot_router.py
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
import json
import asyncio

from app.services import openai_service, query_execution_service
from app.state import USER_SESSIONS, SESSION_THREADS

router = APIRouter()

class ChatMessage(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    response: str

@router.post("/message", response_model=ChatResponse)
async def handle_chat_message(payload: ChatMessage):
    session_id = payload.session_id
    user_message = payload.message
    
    if session_id not in USER_SESSIONS:
        raise HTTPException(status_code=404, detail="Session not initialized. Please upload a CSV file first.")
        
    session_data = USER_SESSIONS[session_id]
    db_path = session_data["db_path"]
    system_prompt = session_data["system_prompt"]
    
    thread_id = openai_service.get_or_create_thread(session_id, SESSION_THREADS)
    
    try:
        run = await openai_service.process_user_message(thread_id, user_message, system_prompt)
        
        while run.status != "completed":
            run = await openai_service.await_run_completion(thread_id, run.id)

            if run.status == "requires_action":
                tool_outputs = []
                for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                    if tool_call.function.name == "run_sql_query":
                        args = json.loads(tool_call.function.arguments)
                        sql_query = args.get("sql_query")
                        print(f"Executing SQL query: {sql_query}")
                        
                        query_result = query_execution_service.run_sql_query(db_path, sql_query)
                        
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": query_result,
                        })
                
                if tool_outputs:
                    run = openai_service.submit_tool_outputs(thread_id, run.id, tool_outputs)
            
            elif run.status == "failed":
                error_message = run.last_error.message if run.last_error else "Unknown error"
                raise HTTPException(status_code=500, detail=f"Assistant run failed: {error_message}")

        response_message = openai_service.get_latest_assistant_response(thread_id)
        return ChatResponse(response=response_message)

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An error occurred in the chat handler: {str(e)}")