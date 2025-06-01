from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from typing import List, Dict

class FAISSAgent:
    """
    A class for managing FAISS (Facebook AI Similarity Search) index operations.
    It uses HuggingFace embeddings to convert text data into vector embeddings
    for efficient similarity search.
    """

    def __init__(self, name: str, max_pages: int = 1):
        """
        Initializes the FAISSAgent with a name and an embedding model.

        Args:
            name (str): The name of the agent.
            max_pages (int): A placeholder for future use, indicating maximum pages to process.
                             Currently not used in the provided methods.
        """
        self.name = name
        self._max_pages = max_pages
        # Initialize the HuggingFace embedding model.
        # This model converts text into numerical vectors.
        self._embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    def build_faiss_index(self, listings: List[Dict], index_path: str = "embeddings/faiss_index"):
        """
        Builds a FAISS index from a list of real estate listings.
        Each listing is converted into a text string and then embedded into a vector.
        The original listing dictionary is stored in the metadata of the FAISS Document.

        Args:
            listings (List[Dict]): A list of dictionaries, where each dictionary represents a listing
                                   and contains keys like 'title', 'place', 'price', 'area', 'details'.
            index_path (str): The local path where the FAISS index will be saved.
        """
        texts = []
        metadatas = [] 
        for item in listings:
            # Concatenate relevant listing information into a single text string for embedding.
            title = str(item.get('title', ''))
            place = str(item.get('place', ''))
            price = str(item.get('price', ''))
            area = str(item.get('area', ''))
            details = str(item.get('details', ''))
            text = f"{title} | {place} | {price} | {area} | {details}"
            texts.append(text)
            metadatas.append(item) 

        # Create a FAISS vector store from the texts, their embeddings, and the associated metadata.
        vectorstore = FAISS.from_texts(texts, self._embedding_model, metadatas=metadatas)
        vectorstore.save_local(index_path)
        print(f"FAISS index built and saved to {index_path}")

    def search_faiss(self, query: str, index_path: str = "embeddings/faiss_index"):
        """
        Searches the FAISS index for listings similar to the given query.

        Args:
            query (str): The search query string.
            index_path (str): The local path where the FAISS index is stored.

        Returns:
            List: A list of Document objects that are most similar to the query.
                  Each Document object will have the original listing dictionary
                  in its 'metadata' attribute.
        """
        try:
            # Load the FAISS index from the specified path.
            vectorstore = FAISS.load_local(
                index_path,
                self._embedding_model,
                allow_dangerous_deserialization=True
            )
            results = vectorstore.similarity_search(query)
            print(f"Search for '{query}' completed. Found {len(results)} results.")
            return results
        except Exception as e:
            print(f"Error searching FAISS index: {e}")
            return []
