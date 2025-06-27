from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import ChatOllama

import time

class RAGPipeline:
    def __init__(self, llm_backend: str = "ollama"):
        # Load sentence-transformer embedding model
        self.embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

        # Load FAISS index
        self.vector_store = FAISS.load_local(
            "vector_index",
            self.embedding,
            allow_dangerous_deserialization=True
        )
        self.retriever = self.vector_store.as_retriever()

        # Select LLM backend
        print("✅ Using Ollama (Mistral or Llama3) as LLM backend")
        self.llmModel = ChatOllama(
            model="mistral",  # or "llama3:8b"
            base_url="http://ollama:11434",
            streaming=True
        )

    async def get_ollama_stream(self, question: str):
        start = time.time()

        # Step 1: Retrieve relevant docs
        docs = self.retriever.invoke(question)
        print(f"FAISS retrieval took: {round(time.time() - start, 2)}s")

        # Step 2: Format prompt with context
        context = "\n\n".join(doc.page_content for doc in docs)
        prompt = (
            f"Use the context below to answer the question.\n\n"
            f"Context: {context}\n\n"
            f"Question: {question}. "
            "Do not say 'context'. Just answer directly. "
            "If you don’t know, politely say you don’t know."
        )

        # Step 3: DEBUG: Check if it's an async or sync generator
        stream_gen = self.llmModel.stream(prompt)
        print("🔍 LLM stream generator type:", type(stream_gen))  # should be <class 'generator'>

        # Step 4: Yield token by token from sync generator
        for chunk in stream_gen:
            yield chunk.content
