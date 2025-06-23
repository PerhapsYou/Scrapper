from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import ChatOllama

import time

llmModel = None  # Initialize llmModel to be used later in the class

class RAGPipeline:
    def __init__(self, llm_backend: str = "ollama"):
        # Load embeddings and vector store
        self.embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vector_store = FAISS.load_local(
            "vector_index",
            self.embedding,
            allow_dangerous_deserialization=True
        )
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 2})

        # Select LLM backend
        print("✅ Using Ollama (llama3) as LLM")
        try:
            self.llmModel = ChatOllama(
                model="llama3:8b", 
                base_url="http://ollama:11434",
                streaming=True  # Enable streaming
                )
        except Exception as e:
                raise RuntimeError("Ollama is not running. Please start it with `ollama run llama3`") from e

    # this method will stream the answer to the question
    def get_ollama_stream(self, question: str):
        start = time.time()

        # ⛔ FAISS retrieval - this is the potential slow part
        docs = self.retriever.get_relevant_documents(question)

        print(f"🔍 FAISS retrieval took: {round(time.time() - start, 2)}s")

        # ⛔ Build context
        context = "\n\n".join(doc.page_content for doc in docs)
        prompt = f"Use the context below to answer the question.\n\nContext: {context}\n\nQuestion: {question}"

        # ✅ Stream LLM response
        for chunk in self.llmModel.stream(prompt):
            yield chunk.content