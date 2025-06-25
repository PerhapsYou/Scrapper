#RAG SERVER
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from langchain_community.embeddings import HuggingFaceEmbeddings
import os # used to get user choice of LLM saved in device environment variable
from contextlib import asynccontextmanager

# local Imports
from rag_pipeline import RAGPipeline  
from build_vector_index import BuildVectorIndex

# # Build Knowledge. Can comment out this section if knowledge already built
# build_vector_index = BuildVectorIndex()
# build_vector_index.run()
 
# Globals for FAISS and pipeline readiness
rag_pipeline = None
faiss_ready = False

# Lifespan handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    global rag_pipeline, faiss_ready

    try:
        print("🚀 Building vector index if not already present...")
        builder = BuildVectorIndex()
        builder.run()

        print("📦 Loading RAG pipeline and FAISS index...")
        llm_backend = os.getenv("LLM_BACKEND", "ollama")
        rag_pipeline = RAGPipeline(llm_backend=llm_backend)

        faiss_ready = True
        print("✅ FAISS and LLM pipeline ready.")
    except Exception as e:
        print(f"❌ Failed during startup: {e}")
        faiss_ready = False

    yield  # Server is now running

    # Optional cleanup code here
    print("🔻 Shutting down RAG server...")

# Initialize FastAPI with lifespan handler
app = FastAPI(lifespan=lifespan)

@app.get("/health")
def health():
    if faiss_ready:
        return {"status": "ok"}
    return JSONResponse(status_code=503, content={"status": "loading"})


@app.post("/chat/stream")
async def stream_response(request: Request):
    if not faiss_ready:
        return JSONResponse(status_code=503, content={"error": "Server not ready"})

    body = await request.json()
    query = body.get("query", "")

    if not query:
        return JSONResponse(status_code=200, content={"responses": [{"query": "No query found in message."}], "events": []})

    async def token_generator():
        for token in rag_pipeline.get_ollama_stream(query):
            yield f"data: {token}\n\n"

    return StreamingResponse(token_generator(), media_type="text/event-stream")


@app.post("/query")
async def query(request: Request):
    if not faiss_ready:
        return JSONResponse(status_code=503, content={"error": "Server not ready"})

    body = await request.json()
    query = body.get("query", "")

    if not query:
        return JSONResponse(status_code=200, content={"responses": [{"query": "No query found in message."}], "events": []})

    response = rag_pipeline.get_ollama_stream(query)
    return JSONResponse(status_code=200, content={"response": response})