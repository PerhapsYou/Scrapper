#RAG SERVER
from fastapi import FastAPI, Request, APIRouter #for db access
import mysql.connector # for db access
from fastapi.responses import JSONResponse
from langchain_community.embeddings import HuggingFaceEmbeddings
import os # used to get user choice of LLM saved in device environment variable
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware # middleware, allowing connection between client and server

# local Imports
from rag_pipeline import RAGPipeline  
from build_vector_index import BuildVectorIndex

from threading import Lock

#signal when to stop RAG response
stop_signal = {"stop": False}
stop_lock = Lock()

# Build Knowledge. Can comment out this section if knowledge already built
build_vector_index = BuildVectorIndex()
build_vector_index.run()


# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # You can use ["*"] for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# now user can choose between LLMs
llm_backend = os.getenv("LLM_BACKEND", "ollama") 
# Initialize RAG pipeline: now RAGPipelines has one argument llm_backend
rag_pipeline = RAGPipeline(llm_backend="ollama")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# db service to get menu items
@app.get("/menu")
def get_menu():
    try:
        db= mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="navi-bot"
        )
        cursor = db.cursor()
        cursor.execute("SELECT id,title, emoji, content FROM menu_item")
        menu_items = cursor.fetchall()
        cursor.close()
        db.close()
        return {"menu": menu_items}
    except Exception as e:
        print("Error occurred:", e)
        return {"error": str(e)}

@app.get('/')
def read_root():
    return {"message": "Welcome to the RAG API. Use the /query endpoint to ask questions."}    

@app.post("/chat/stream")
async def stream_response(request: Request):
    body = await request.json()
    print("Received body:", body)  

    # Extract query from tracker
    query = body.get("query", "")

    if not query:
        return JSONResponse(
            status_code=200,
            content={"responses": [{"query": "No query found in message."}], "events": []}
        )
        
     # Reset stop flag before each new generation
    with stop_lock:
        stop_signal["stop"] = False
        
    # Token generator will not work when user asks the bot to stop RAG response
    async def token_generator():
        for token in rag_pipeline.get_ollama_stream(query):
            with stop_lock:
                if stop_signal["stop"]:
                    break
            yield f"data: {token}\n\n"

    return StreamingResponse(token_generator(), media_type="text/event-stream")

@app.post("/query")
async def query(request: Request):
    body = await request.json()
    print("Received body:", body) 

    # Extract query from tracker
    query = body.get("query", "")

    if not query:
        return JSONResponse(
            status_code=200,
            content={"responses": [{"query": "No query found in message."}], "events": []}
        )

    # 👇 RAG PIPELINE IMPLE
    response = rag_pipeline.get_ollama_stream(query)
    print(response)
    response = JSONResponse(
        status_code=200,
        content={"response" : response.get("result", "no answer found.")} 
        )
    print(response)

    return response

#when user clicks on stop button, stop RAG respose
@app.post("/stop")
async def stop_generation():
    with stop_lock:
        stop_signal["stop"] = True
    return {"status": "stop requested"}