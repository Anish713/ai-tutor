from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.utils import filter_complex_metadata
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import chroma
from langchain_community.embeddings import fastembed
import os

class ChunkVectorStore:
    def __init__(self, persist_directory):
        self.persist_directory = persist_directory
        self.embedding = fastembed.FastEmbedEmbeddings()
    
    def split_into_chunks(self, file_path: str):
        doc = PyPDFLoader(file_path).load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
        chunks = text_splitter.split_documents(doc)
        chunks = filter_complex_metadata(chunks)
        return chunks
    
    def store_to_vector_database(self, chunks):
        return chroma.Chroma.from_documents(
            documents=chunks,
            embedding=self.embedding,
            persist_directory=self.persist_directory
        )
    
    def load_existing_database(self):
        if os.path.exists(self.persist_directory):
            return chroma.Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embedding
            )
        return None

def process_pdf(file_path, db_name):
    vector_store = ChunkVectorStore(db_name)
    
    # Split PDF into chunks
    chunks = vector_store.split_into_chunks(file_path)
    
    # Store chunks in Chroma database
    db = vector_store.store_to_vector_database(chunks)
    db.persist()
    
    print(f"Embeddings for {file_path} stored in {db_name}")

def main():
    pdf_files = [
        "D:\\FuseMachine\\DataSet_RAG\\Data_basic.pdf"
        "D:\\FuseMachine\\DataSet_RAG\\Data_intermediate.pdf"
        #"D:\\FuseMachine\\DataSet_RAG\\what-is-ai-v2.pdf"
    ]
    
    for i, pdf_file in enumerate(pdf_files, 1):
        db_name = f"chroma_db_{i}"
        process_pdf(pdf_file, db_name)

if __name__ == "__main__":
    main()