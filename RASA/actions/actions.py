# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
import requests,sseclient
import pymysql
from rasa_sdk.executor import CollectingDispatcher
from typing import Any,Dict,List

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "navi-bot"
}
class ActionShowMenu(Action):
    def name(self) -> str:
        return "action_show_menu"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        cursor.execute("SELECT title, emoji FROM menu_item")
        results = cursor.fetchall()
        connection.close()

        if not results:
            dispatcher.utter_message("Sorry, the menu is currently unavailable.")
            return []

        menu_text = "\n".join(f"{emoji} {title}" for title, emoji in results)
        print("[debug menu items]", menu_text)
        dispatcher.utter_message(text=f"Here are the available options:\n{menu_text}")
        return []

class ActionRAGFallback(Action):
    def name(self) -> str:
        return "action_rag_fallback"
    
    async def run(self, dispatcher: "CollectingDispatcher", 
            tracker: Tracker, 
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        user_message = tracker.latest_message.get("text")

        # Call the RAG service
        #rag_response 
        rag_url = "http://rag_server:8000/chat/stream"
        try:
            response = requests.post(
                rag_url, 
                json={"query": user_message},
                stream=True)
            
            
            sse_client = sseclient.SSEClient(response)
            full_answer = ""
            for event in sse_client.events():
                if event.data == "[DONE]":
                    break
                full_answer += event.data

            dispatcher.utter_message(text=full_answer)
            return []
        except requests.exceptions.RequestException as e:
            rag_response = f"Error connecting to RAG service: {str(e)}"

        # Send the response back to the user
        dispatcher.utter_message(text=rag_response)

        return []
    
    def send_stop_signal():
        try:
            requests.post("http://rag_server:8000/stop")
        except Exception as e:
            print("Failed to send stop signal:", str(e))
    