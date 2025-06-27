# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import requests
import sseclient
import pymysql

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --- FastAPI setup ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for dev; restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DB connection ---
def get_db_connection():
    return pymysql.connect(
        host='db',
        user='root',
        password='root',
        database='navi-bot',
        cursorclass=pymysql.cursors.DictCursor
    )

# --- FastAPI endpoint for menu ---
@app.get("/menu")
async def get_menu():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, emoji, content FROM menu_item")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return {"menu": rows}


# --- Custom RAG Fallback Action ---
class ActionRAGFallback(Action):
    def name(self) -> str:
        return "action_rag_fallback"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        user_message = tracker.latest_message.get("text", "").strip().lower()

        # Optional: skip RAG trigger for generic menu/help commands
        if user_message in ["menu", "show menu", "help", "options"]:
            dispatcher.utter_message(text="You can click the menu icon or type a question.")
            return []

        # 🚨 Instead of contacting RAG directly, send a signal to frontend to handle it
        dispatcher.utter_message(json_message={"stream_from_rag": True, "query": user_message})

        return []