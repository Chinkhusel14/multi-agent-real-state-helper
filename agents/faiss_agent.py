from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

class FAISSAgent:
    def __init__(self, name: str, max_pages: int = 1):
        self.name = name
        self._max_pages = max_pages
        self._embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    def build_faiss_index(self, listings: list, index_path: str = "embeddings/faiss_index"):
        texts = []
        for item in listings:
            text = f"{item['title']} | {item['place']} | {item['price']} | {item['area']} | {item['details']}"
            texts.append(text)

        vectorstore = FAISS.from_texts(texts, self._embedding_model)
        vectorstore.save_local(index_path)

    def search_faiss(self, query: str, index_path: str = "embeddings/faiss_index"):
        vectorstore = FAISS.load_local(
            index_path,
            self._embedding_model,
            allow_dangerous_deserialization=True  
        )
        return vectorstore.similarity_search(query)

