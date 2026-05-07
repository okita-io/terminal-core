import json
from pathlib import Path

import chromadb


class FeedbackStore:
    """Persistent per-game ChromaDB store for round feedback summaries."""

    def __init__(self, sessions_dir: str, game_id: str):
        db_path = str(Path(sessions_dir) / game_id / "vectordb")
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(
            name="feedback",
            metadata={"hnsw:space": "cosine"},
        )
        self.game_id = game_id

    def add_round(self, round_n: int, summary: str, metadata: dict | None = None):
        # Design rounds use negative integers, code rounds use non-negative
        prefix = "design" if round_n < 0 else "round"
        doc_id = f"{prefix}_{abs(round_n):04d}"
        meta = {"round": round_n, "game_id": self.game_id}
        if metadata:
            # ChromaDB metadata values must be str/int/float/bool
            for k, v in metadata.items():
                meta[k] = v if isinstance(v, (str, int, float, bool)) else json.dumps(v)

        existing = self.collection.get(ids=[doc_id])
        if existing["ids"]:
            self.collection.update(documents=[summary], ids=[doc_id], metadatas=[meta])
        else:
            self.collection.add(documents=[summary], ids=[doc_id], metadatas=[meta])

    def query_similar(self, query: str, n: int = 5) -> list[dict]:
        total = self.collection.count()
        if total == 0:
            return []
        results = self.collection.query(
            query_texts=[query],
            n_results=min(n, total),
        )
        return [
            {"document": doc, "metadata": meta, "distance": dist}
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            )
        ]

    def get_all_summaries(self) -> list[str]:
        return self.collection.get().get("documents", [])
