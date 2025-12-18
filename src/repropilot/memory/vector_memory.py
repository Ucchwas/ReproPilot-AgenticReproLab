from __future__ import annotations
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer


MEM_SCHEMA = """
CREATE TABLE IF NOT EXISTS mem_chunks(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id TEXT,
  chunk TEXT,
  embedding BLOB
);
"""


@dataclass
class VectorMemory:
    db_path: str
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"

    def __post_init__(self) -> None:
        self._encoder = SentenceTransformer(self.model_name)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(MEM_SCHEMA)

    def add_chunks(self, run_id: str, chunks: list[str]) -> None:
        embs = self._encoder.encode(chunks, normalize_embeddings=True)
        with sqlite3.connect(self.db_path) as conn:
            for chunk, emb in zip(chunks, embs):
                conn.execute(
                    "INSERT INTO mem_chunks(run_id, chunk, embedding) VALUES(?, ?, ?)",
                    (run_id, chunk, emb.astype(np.float32).tobytes()),
                )

    def search(self, run_id: str, query: str, k: int = 6) -> list[str]:
        q = self._encoder.encode([query], normalize_embeddings=True)[0].astype(np.float32)
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT chunk, embedding FROM mem_chunks WHERE run_id=?",
                (run_id,),
            ).fetchall()

        if not rows:
            return []

        chunks = []
        mat = []
        for chunk, emb_blob in rows:
            chunks.append(chunk)
            mat.append(np.frombuffer(emb_blob, dtype=np.float32))
        M = np.vstack(mat)  # (n, d)
        sims = M @ q  # cosine since normalized
        top_idx = np.argsort(-sims)[:k]
        return [chunks[i] for i in top_idx]
