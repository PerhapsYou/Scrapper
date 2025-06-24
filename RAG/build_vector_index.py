from langchain_community.vectorstores.faiss import FAISS
import faiss
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

from langchain_community.document_loaders import DirectoryLoader
from langchain.docstore.in_memory import InMemoryDocstore

import numpy as np
import os

# #message box asking whether or not user wants to scrape the web, pdfs, and images
# import tkinter as tk
# from tkinter import messagebox

#calling scrapers into this pipeline
from scrapers.web_scraper import run_scraper 
from scrapers.pdf_scraper import scan_all_pdfs
from scrapers.image_scraper import scan_images
from scrapers.pdf_scraper import PDFScraper

DIR = "knowledge"  # Directory where text files are stored

# def ask_user(title, question):
#     root = tk.Tk()
#     root.withdraw()
#     answer = messagebox.askyesno(title, question)
#     root.destroy()
#     return answer

class BuildVectorIndex:
    def run(self):
        # # 1. Ask for web scraping
        # if ask_user("Web Scraping Confirmation", "Do you want to run web scraping before scanning PDFs and images?"):
        run_scraper(urls_path="urls.txt", output_dir=DIR, depth=2)
        # else:
        #     print("[Skip] Web scraping skipped.")

        # # 2. Ask for PDF scanning
        # if ask_user("PDF Scanning Confirmation", "Do you want to scan PDFs in the knowledge folder?"):
        scan_all_pdfs()
        # else:
        #     print("[Skip] PDF scanning skipped.")

        # 3. Always run image scanning
        scan_images(folder=DIR)

        # 4. Load all .txt files and build vector index
        loader = DirectoryLoader(
            DIR,
            glob="**/*.txt",
            loader_cls=lambda path: TextLoader(path, encoding="utf-8")
        )
        documents = loader.load()

        if not documents:
            raise ValueError("No documents found. Please check the directory and file format.")
        
        print("\n[INFO] The following .txt files were loaded:")
        for doc in documents:
            print(f" - {doc.metadata.get('source', 'Unknown source')}")
        
        cSize = 300
        cOverlap = 100
        #editing chunk size and overlap
        splitter = CharacterTextSplitter(chunk_size=cSize, chunk_overlap=cOverlap)
        print("building vector index with chunk size", cSize, "and chunk overlap", cOverlap)
        chunks = splitter.split_documents(documents)

        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cuda"}
        )
        
        texts = [chunk.page_content for chunk in chunks]
        embeddings = embedding_model.embed_documents(texts)  # returns List[List[float]]

        print(f"[INFO] Embedding {len(embeddings)} chunks...")

        # FAISS on GPU
        dim = len(embeddings[0])
        cpu_index = faiss.IndexFlatL2(dim)
        
        res = faiss.StandardGpuResources()
        gpu_index = faiss.index_cpu_to_gpu(res, 0, cpu_index)
        gpu_index.add(np.array(embeddings).astype("float32"))
        print(f"[INFO] FAISS index populated with {gpu_index.ntotal} vectors on GPU.")

        # Create docstore and mapping from index to doc IDs
        docstore = InMemoryDocstore({str(i): doc for i, doc in enumerate(chunks)})
        index_to_docstore_id = {i: str(i) for i in range(len(chunks))}

        # Build FAISS vector store using GPU index and docstore
        vector_store = FAISS(
            embedding_function=embedding_model,
            index=gpu_index,
            docstore=docstore,
            index_to_docstore_id=index_to_docstore_id
        )

        # Save vector store locally, but
        # Convert GPU index back to CPU for saving
        cpu_index_for_save = faiss.index_gpu_to_cpu(gpu_index)
        vector_store.index = cpu_index_for_save  # Replace index with CPU version before saving
        vector_store.save_local("vector_index")

        print("Vector index built and saved to 'vector_index/'")

if __name__ == "__main__":
    builder = BuildVectorIndex()
    builder.run()
