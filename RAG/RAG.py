from .Vector_store import ChunkVectorStore as cvs
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOllama
import os

class rag:
    def __init__(self, persist_directory):
        self.csv_obj = cvs(persist_directory)
        self.vector_store = None
        self.retriever = None
        self.chain = None
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
        self.model = ChatOllama(model="anishstha245/phi3_gsm8k:latest")
        
        self.vector_store = self.csv_obj.load_existing_database()
        if self.vector_store:
            self.set_retriever()
            self.augment()

    def set_retriever(self):
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "k": 3,
                "score_threshold": 0.5,
            },
        )

    def augment(self):
        self.chain = (
            {"context": self.retriever, "question": RunnablePassthrough()}
            | self.prompt
            | self.model
            | StrOutputParser()
        )

    def ask(self, query: str, context: list = None):
        if not self.chain:
            return "Could not generate a response. The knowledge base might be empty."
        
        context_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in context]) if context else ""
        prompt_with_context = f"{context_str}\n\nQuestion: {query}"

        return self.chain.invoke(prompt_with_context)

    def feed(self, file_path: str):
        chunks = self.csv_obj.split_into_chunks(file_path)
        if self.vector_store is None:
            self.vector_store = self.csv_obj.store_to_vector_database(chunks)
        else:
            self.vector_store.add_documents(chunks)
        
        self.vector_store.persist()
        self.set_retriever()
        self.augment()

    def clear(self):
        if os.path.exists(self.csv_obj.persist_directory):
            import shutil
            shutil.rmtree(self.csv_obj.persist_directory)
        self.vector_store = None
        self.chain = None
        self.retriever = None
        print("Database cleared. You can now feed new data.")