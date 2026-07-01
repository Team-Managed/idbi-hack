import asyncio
import os
from qdrant_client import AsyncQdrantClient, models
from fastembed import TextEmbedding, SparseTextEmbedding

COLLECTION_NAME = "financial_docs"

_client = AsyncQdrantClient(
    url=os.getenv("QDRANT_URL", "http://localhost:6333"),
    api_key=os.getenv("QDRANT_API_KEY")
)
_dense_model = TextEmbedding("BAAI/bge-small-en-v1.5")
_sparse_model = SparseTextEmbedding("Qdrant/bm25")

async def search_financial_docs(query: str, limit: int = 5):
    dense_vec, sparse_vec = await asyncio.gather(
        asyncio.to_thread(lambda: list(_dense_model.embed([query]))[0]),
        asyncio.to_thread(lambda: list(_sparse_model.embed([query]))[0]),
    )

    results = await _client.query_points(
        collection_name=COLLECTION_NAME,
        prefetch=[
            models.Prefetch(query=dense_vec.tolist(), using="dense", limit=20),
            models.Prefetch(
                query=models.SparseVector(
                    indices=sparse_vec.indices.tolist(),
                    values=sparse_vec.values.tolist(),
                ),
                using="sparse",
                limit=20,
            ),
        ],
        query=models.FusionQuery(fusion=models.Fusion.RRF),
        limit=limit,
    )

    return [
        {"source": p.payload.get("source"), "content": p.payload.get("content")}
        for p in results.points
    ]
