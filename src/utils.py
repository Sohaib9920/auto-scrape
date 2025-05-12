from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage
from typing import List
import os


def store_conversation(messages: List[BaseMessage], step):
    result = ""
    for msg in messages:
        if isinstance(msg, HumanMessage):
            result += f"Human: {msg.content[0]['text'] if isinstance(msg.content, list) else msg.content}\n"
        elif isinstance(msg, SystemMessage):
            result += f"System: {msg.content}\n"
        elif isinstance(msg, AIMessage):
            result += f"AI: {msg.content}\n"

    os.makedirs("temp", exist_ok=True)
    with open(f"temp/{step}.txt", "w", encoding="utf-8") as f:
        f.write(result)
