    #RAG SERVER
from fastapi import FastAPI, Request, HTTPException, Body #for db access
from fastapi.responses import JSONResponse
import os # used to get user choice of LLM saved in device environment variable
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware # middleware, allowing connection between client and server
import pymysql # for db access
# local Imports
from rag_pipeline import RAGPipeline  
from build_vector_index import BuildVectorIndex
import bcrypt

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


# Utility: database connection
def get_db_connection():
    return pymysql.connect(
        host="host.docker.internal", 
        user="root",
        password="root",
        database="navi-bot",
        cursorclass=pymysql.cursors.DictCursor
    )

# now user can choose between LLMs
llm_backend = os.getenv("LLM_BACKEND", "ollama") 
# Initialize RAG pipeline: now RAGPipelines has one argument llm_backend
rag_pipeline = RAGPipeline(llm_backend="ollama")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# The menu route
@app.get("/menu")
async def get_menu():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, emoji, content FROM menu_item")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return {"menu": rows}
    except Exception as e:
        print("DB Error:", e)  # This will print to your console
        raise HTTPException(status_code=500, detail="Failed to fetch menu data")


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

    if ("I don't know" in response):
        with open("knowledge/unknown.txt", "w") as file:
            file.write(query)
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

# admin login
@app.post("/login")
async def login(request: Request):
    body = await request.json()
    username = body.get("username")
    password = body.get("password")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM accounts WHERE username=%s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
            return {"status": "success", "message": "Login successful"}
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        print("Login error:", e)
        raise HTTPException(status_code=500, detail="Internal server error")
    
# Admin: CRUDS
@app.get("/admin/menu")
async def get_menu_items():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, emoji, content FROM menu_item")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return {"menu": rows}
    except Exception as e:
        print("Menu fetch error:", e)
        raise HTTPException(status_code=500, detail="Failed to fetch menu data")

# POST new menu item
@app.post("/admin/menu")
async def add_menu_item(data: dict = Body(...)):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO menu_item (title, emoji, content) VALUES (%s, %s, %s)",
            (data["title"], data["emoji"], data["content"])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"status": "success"}
    except Exception as e:
        print("Insert error:", e)
        raise HTTPException(status_code=500, detail="Failed to add menu item")

# PUT update menu item
@app.put("/admin/menu/{item_id}")
async def update_menu_item(item_id: int, data: dict = Body(...)):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE menu_item SET title=%s, emoji=%s, content=%s WHERE id=%s",
            (data["title"], data["emoji"], data["content"], item_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"status": "updated"}
    except Exception as e:
        print("Update error:", e)
        raise HTTPException(status_code=500, detail="Failed to update menu item")

# DELETE menu item
@app.delete("/admin/menu/{item_id}")
async def delete_menu_item(item_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM menu_item WHERE id=%s", (item_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return {"status": "deleted"}
    except Exception as e:
        print("Delete error:", e)
        raise HTTPException(status_code=500, detail="Failed to delete menu item")