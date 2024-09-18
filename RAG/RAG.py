from .Vector_store import ChunkVectorStore as cvs
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOllama
import os
import requests

class rag:
    def __init__(self, persist_directory):
        # Initialize vector store and retriever
        self.csv_obj = cvs(persist_directory)
        self.vector_store = None
        self.retriever = None
        self.chain = None
        self.summarizer = ChatOllama(model="anishstha245/phi3_gsm8k:latest")
        self.prompt = PromptTemplate.from_template(
            """
            <s> [INST] You are an assistant for question-answering tasks. Use the following pieces of retrieved context
            to answer the question. If you don't know the answer, just say that you are not aware. Use three sentences
            maximum and keep the answer concise. [/INST] </s>
            [INST] Question: {question}
            Context: {context}
            Answer: [/INST]
            """
        )

        # Initialize the chat model
        self.model = ChatOllama(model="anishstha245/phi3_gsm8k:latest")
        
        # Load vector store from the given directory
        self.vector_store = self.csv_obj.load_existing_database()
        if self.vector_store:
            self.set_retriever()
            self.augment()

    def set_retriever(self):
        # Configure the retriever to search for similar documents in the vector store
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "k": 3,
                "score_threshold": 0.5,
            },
        )
    
    def get_response_from_api(self, prompt):
        # API call to the language model
        data = {
            "model": "anishstha245/phi3_gsm8k:latest",
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {
               "temperature": 0.7,
                "repeat_penalty": 1.0,
                "seed": 3407,
                "top_k": 50,
                "top_p": 1.0,
            },
        }
        
        API_URL = "http://localhost:11434/api/chat"
        HEADERS = {"Content-Type": "application/json"}
        
        # Make the request to the API
        response = requests.post(API_URL, json=data, headers=HEADERS)
        if response.status_code == 200:
            return response.json().get("message", {}).get("content", "No content")
        else:
            return f"Error: {response.status_code}"

    def augment(self):
        # Augment the model with retrieval and summarization capabilities
        self.chain = (
            {"context": self.retriever, "question": RunnablePassthrough()}
            | self.prompt
            | self.model
            | StrOutputParser()
        )



    def ask(self, query: str, context: list = None):
        # Retrieve the most relevant summaries instead of full documents
        if not self.chain:
            return "Could not generate a response. The knowledge base might be empty."

        # Retrieve summaries from the vector store
        results = self.vector_store.similarity_search(query, k=3)
        
        # Prepare context from summaries
        context_str = ""
        for doc in results:
            # Use the summary if available
            if doc.metadata.get("type") == "summary":
                context_str += f"\nSummary: {doc.page_content}\n"
            else:
                context_str += f"\nDocument: {doc.page_content}\n"

        # Combine query and context for prompt
        prompt_with_context = f"{context_str}\n\nQuestion: {query}"

        return self.chain.invoke(prompt_with_context)

    
    

    def feed(self, file_path: str):
        # Feed new PDF content, split it, and generate summaries
        chunks = self.csv_obj.split_into_chunks(file_path)
        summarized_chunks = []
        
        # Generate summaries for each chunk and store in vector database
        for chunk in chunks:
            summary = self.generate_summary(chunk.page_content)
            summarized_chunk = {
                "page_content": summary,
                "metadata": {"type": "summary", "original_chunk": chunk.page_content}
            }
            summarized_chunks.append(summarized_chunk)
        
        # Store summaries and original content in the vector database
        if self.vector_store is None:
            self.vector_store = self.csv_obj.store_to_vector_database(summarized_chunks)
        else:
            self.vector_store.add_documents(summarized_chunks)
        
        # Persist the updated vector database and set retriever
        self.vector_store.persist()
        self.set_retriever()
        self.augment()
    
    def generate_summary(self, content: str) -> str:
        # Summarize the content
        summary_prompt = f"Summarize the following content in 3 sentences: {content}"
        summary = self.summarizer.get_response_from_api(summary_prompt)
        return summary

    def clear(self):
        # Clear the existing vector store by deleting the persistence directory
        if os.path.exists(self.csv_obj.persist_directory):
            import shutil
            shutil.rmtree(self.csv_obj.persist_directory)
        self.vector_store = None
        self.chain = None
        self.retriever = None
        print("Database cleared. You can now feed new data.")

    def get_level_description(self):
        # Retrieve a description for the level based on the stored documents in the vector store
        if not self.vector_store:
            return "No description available. The database might be empty."
        
        # Retrieve the most representative content for the level description
        description_docs = self.vector_store.similarity_search(query="overview", k=1)
        if description_docs:
            return description_docs[0].page_content
        else:
            return "No description available."