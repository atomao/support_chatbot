import asyncio
import os
import sys
from pathlib import Path

import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from pydantic import BaseModel, ValidationError
from shop_agents.database import history

sys.path.append(Path(".").resolve().parent.parent.parent)   

from shop_agents import manager_agent
from agents import Runner


class ChatRequest(BaseModel):
    message: str
    session_id: str
    user_id: str


class ChatResponse(BaseModel):
    answer: str


class UserInfo(BaseModel):
    user_id: str
    session_id: str


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}) 


@app.post("/api/support/chat")
def chat():
    """Main support-chat endpoint."""
    try:
        req = ChatRequest(**request.json)
    except ValidationError as e:
        return jsonify({"detail": e.errors()}), 422

    user = UserInfo(
        req.user_id, req.session_id
    )
    history.add_user_message(req.session_id, req.message)
    messages = history.get_history(req.session_id)
    assistant_output =(Runner.run_sync(manager_agent, input=messages, context = user)).final_output
    history.add_assistant_message(req.session_id, assistant_output)

    return jsonify(ChatResponse(answer=assistant_output).dict())



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
