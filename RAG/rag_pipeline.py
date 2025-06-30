from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import ChatOllama
import torch

import time

llmModel = None  # Initialize llmModel to be used later in the class

class RAGPipeline:
    def __init__(self, llm_backend: str = "ollama"):
        # Load embeddings and vector store
        self.embedding = HuggingFaceInstructEmbeddings(
             model_name="hkunlp/instructor-xl",
            # If you have a GPU, set device to "cuda", otherwise use "cpu"
             model_kwargs={"device": "cuda" if torch.cuda.is_available() else "cpu"} 
             )
        self.vector_store = FAISS.load_local(
            "vector_index",
            self.embedding,
            allow_dangerous_deserialization=True
        )
        self.retriever = self.vector_store.as_retriever()

        # Select LLM backend
        print("✅ Using Ollama (llama3) as LLM")
        try:
            self.llmModel = ChatOllama(
                model="tuned-model", 
                base_url="http://ollama:11434",
                streaming=True  # Enable streaming
                )
            print("Connecting to Ollama at:", self.llmModel.base_url)
        except Exception as e:
                raise RuntimeError("Ollama is not running. Please start it with `ollama run llama3`") from e
    

    # this method will stream the answer to the question
    def get_ollama_stream(self, question: str):
        start = time.time()

        docs = self.retriever.invoke(question)

        print(f"FAISS retrieval took: {round(time.time() - start, 2)}s")

        context = "\n\n".join(doc.page_content for doc in docs)
        print(context)
        prompt = f"Use the context below to answer the question.\n\nContext: {context}\n\nQuestion: {question}. Do not say context just give me an answer. If you do not know just apologize and say you do not know.."

        for chunk in self.llmModel.stream(prompt):
            yield chunk.content