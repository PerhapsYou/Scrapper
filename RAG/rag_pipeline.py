from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import ChatOllama
import torch

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

        # Select LLM backend
        print("✅ Using Ollama (llama3) as LLM")
        try:
            self.llmModel = ChatOllama(
                model="llama3", 
                base_url="http://ollama:11434",
                temperature=0.5,
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

        for chunk in self.llmModel.stream(prompt):
            yield chunk.content