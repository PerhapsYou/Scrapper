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
        host='localhost',
        user='root',
        password='',
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

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_message = tracker.latest_message.get("text", "").strip().lower()

        # Avoid sending common menu/help keywords to RAG
        if user_message in ["menu", "show menu", "help", "options"]:
            dispatcher.utter_message(text="You can click the menu icon or type a question.")
            return []

        try:
            rag_url = "http://rag_server:8000/chat/stream"
            response = requests.post(
                rag_url,
                json={"query": user_message},
                stream=True
            )

            sse_client = sseclient.SSEClient(response)
            full_answer = ""
            for event in sse_client.events():
                if event.data == "[DONE]":
                    break
                full_answer += event.data

            dispatcher.utter_message(text=full_answer)
        except requests.exceptions.RequestException as e:
            dispatcher.utter_message(text=f"Error connecting to RAG service: {str(e)}")

        return []
