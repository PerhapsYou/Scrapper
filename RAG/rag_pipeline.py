from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import ChatOllama
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_core.output_parsers import StrOutputParser
import torch
import uuid
import os
import posthog
import streamlit as st

import time

llmModel = None  # Initialize llmModel to be used later in the class

class RAGPipeline:
    def __init__(self, llm_backend: str = "ollama"):
        # Load embeddings and vector store
        self.embedding = HuggingFaceEmbeddings(
             model_name="sentence-transformers/all-MiniLM-L6-v2",
            # If you have a GPU, set device to "cuda", otherwise use "cpu"
             model_kwargs={"device": "cuda" if torch.cuda.is_available() else "cpu"} 
             )
        self.vector_store = FAISS.load_local(
            "vector_index",
            self.embedding,
            allow_dangerous_deserialization=True
        )
        self.retriever = self.vector_store.as_retriever(k=5)
        try:
            posthog.api_key = os.environ["POSTHOG_API_KEY"]
            posthog.host = os.environ['POSTHOG_HOST']
        except KeyError:
            raise ValueError("Please set POSTHOG_API_KEY and POSTHOG_HOST environment variables")

        try:
            # Select LLM backend
            print("Using Ollama (llama3) as LLM")
            self.llmModel = ChatOllama(
                model="llama3", 
                base_url="http://ollama:11434",
                temperature=0.5,
                streaming=True  # Enable streaming
                )
            self.memory = ConversationBufferMemory()
            self.chain = ConversationChain(llm=self.llmModel, memory=self.memory, verbose=True)
            
            print("Connecting to Ollama at:", self.llmModel.base_url)
        except Exception as e:
                raise RuntimeError("Ollama is not running. Please start it with `ollama run llama3`") from e
    
    def predict(message: str, distinct_id: str, session_id: str) -> str:
        # 1. Call Rasa
        try:
            response = requests.post(
                "http://localhost:5005/webhooks/rest/webhook",
                json={"sender": distinct_id, "message": message},
                timeout=10
            )
            rasa_response = response.json()
        except Exception as e:
            print(f"Error calling Rasa: {e}")
            return "Sorry, I couldn't reach the assistant."

        # 2. Extract Rasa response
        reply_text = rasa_response[0].get("text", "No response.") if rasa_response else "No response."

        # 3. Track in PostHog
        try:
            task(
                distinct_id=distinct_id,
                input=message,
                output=reply_text,
                session_id=session_id,
                properties={"source": "rasa-web-client"}
            )
        except Exception as e:
            print(f"PostHog tracking failed: {e}")

        return reply_text
    

    def task(distinct_id, input, output, event="llm-task", timestamp=None, session_id=None, properties=None):
        props = properties if properties else {}
        props["$llm_input"] = input
        props["$llm_output"] = output

        if session_id:
            props["$session_id"] = session_id

        posthog.capture(
            distinct_id=distinct_id, event=event, properties=props, timestamp=timestamp, disable_geoip=False
        )


    def get_ollama_stream(self, question: str, prevQuestion: str = ""):
        start = time.time()

        docs = self.retriever.invoke(question)

        print(f"FAISS retrieval took: {round(time.time() - start, 2)}s")

        context = "\n\n".join(doc.page_content for doc in docs)

        if (prevQuestion == ""):
            prompt = f"""Answer the question using only the information provided below.
                    Context:
                    {context}

                    Question:
                    {question}

                    Instructions:
                    - Answer the question without adding any introductory or concluding phrases. 
                    - Do not repeat or refer to the context.
                    - If the answer cannot be determined from the context, respond with: "I'm sorry, I don't know." 
                    - Be concise and accurate.
                    - In writing your answer make sure there are no dashes.
                    - Return your response as markdown.
                    - Do not output in a single paragraph.
                    - Use dashes instead of asterisks in the markdown.
                """
        else:
            print("PREVIOUS QUESTIONS: " , prevQuestion)
            prompt = f"""Answer the question using only the information provided below.
                    Previous Questions:
                        {prevQuestion}

                    Context:
                    {context}

                    Question:
                    {question}

                    Instructions:
                    - Answer the question without adding any introductory or concluding phrases. 
                    - Do not repeat or refer to the context.
                    - If the answer cannot be determined from the context, respond with: "I'm sorry, I don't know." 
                    - In writing your answer make sure there are no dashes.
                    - Return your response as markdown.
                    - Do not output in a single paragraph.
                    - Use dashes instead of asterisks in the markdown.
                    - Use previous questions to provide more context.
                """    
        response = self.chain.invoke({"input": prompt})
        return response["response"]

    # # this method will stream the answer to the question
    # def get_ollama_stream(self, question: str, prevQuestion: str = ""):
    #     start = time.time()

    #     docs = self.retriever.invoke(question)

    #     print(f"FAISS retrieval took: {round(time.time() - start, 2)}s")

    #     context = "\n\n".join(doc.page_content for doc in docs)

    #     if (prevQuestion == ""):
    #         prompt = f"""Answer the question using only the information provided below.
    #                 Context:
    #                 {context}

    #                 Question:
    #                 {question}

    #                 Instructions:
    #                 - Answer the question without adding any introductory or concluding phrases. 
    #                 - Do not repeat or refer to the context.
    #                 - If the answer cannot be determined from the context, respond with: "I'm sorry, I don't know." 
    #                 - Be concise and accurate.
    #                 - In writing your answer make sure there are no dashes.
    #                 - Return your response as markdown.
    #                 - Do not output in a single paragraph.
    #                 - Use dashes instead of asterisks in the markdown.
    #             """
    #     else:
    #         print("PREVIOUS QUESTIONS: " , prevQuestion)
    #         prompt = f"""Answer the question using only the information provided below.
    #                 Previous Questions:
    #                     {prevQuestion}

    #                 Context:
    #                 {context}

    #                 Question:
    #                 {question}

    #                 Instructions:
    #                 - Answer the question without adding any introductory or concluding phrases. 
    #                 - Do not repeat or refer to the context.
    #                 - If the answer cannot be determined from the context, respond with: "I'm sorry, I don't know." 
    #                 - In writing your answer make sure there are no dashes.
    #                 - Return your response as markdown.
    #                 - Do not output in a single paragraph.
    #                 - Use dashes instead of asterisks in the markdown.
    #                 - Use previous questions to provide more context.
    #             """    
    #     print(self.llmModel.invoke(prompt))
    #     print(self.llmModel.invoke(prompt.get('content')))
    #     return self.llmModel.invoke(prompt).get('content')


        