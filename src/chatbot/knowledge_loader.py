from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

def build_knowledge_base():
    docs = []
    
    # docs += PyPDFLoader().load()
    docs += TextLoader("D:/code/Django/App/src/chatbot/data.txt", encoding="utf-8").load()
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=80
    )
    
    chunks = splitter.split_documents(docs)
    
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )
    
    db = Chroma.from_documents(
        chunks,
        embedding=embeddings,
        persist_directory="kb"
    )
    
    print("Knowledge base built")
    
    
    # python manage.py shell
    # from chatbot.knowledge_loader import build_knowledge_base()
    # build_knowledge_base()