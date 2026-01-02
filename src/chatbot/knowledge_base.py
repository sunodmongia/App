from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

db = Chroma(
    persist_directory='kb',
    embedding_function=embeddings
)

def get_company_context(query, k=4):
    docs = db.similarity_search(query, k=k)
    return "\n\n".join(d.page_content for d in docs)