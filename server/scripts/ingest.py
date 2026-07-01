import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, SparseVectorParams

COLLECTION_NAME = "financial_docs"

def init_qdrant():
    client = QdrantClient(url=os.getenv("QDRANT_URL", "http://localhost:6333"))

    if client.collection_exists(COLLECTION_NAME):
        print(f"Collection '{COLLECTION_NAME}' already exists — skipping creation.")
        return

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config={
            "dense": VectorParams(size=384, distance=Distance.COSINE),
        },
        sparse_vectors_config={
            "sparse": SparseVectorParams(),
        },
    )
    print(f"Collection '{COLLECTION_NAME}' created with dense + sparse vector support.")

if __name__ == "__main__":
    init_qdrant()
