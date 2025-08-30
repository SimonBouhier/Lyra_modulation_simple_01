# lyra/modules/vectorsonde.py

from lyra.base import LyraModule
from sentence_transformers import SentenceTransformer
import numpy as np

class VectorSonde(LyraModule):
    """🧭 VectorSonde — Encodeur vectoriel latéral basé sur all-MiniLM."""

    def __init__(self, name, params, neighbors=None):
        super().__init__(name, params, neighbors)
        self.encoder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.vectors = []  # [(timestamp, vector, metadata)]
        self.max_length = self.params.get("max_length", 100)

    def intrinsic(self, t: float) -> float:
        """Pas de dynamique intrinsèque : mémoire vectorielle passive."""
        return 0.0

    def encode_and_store(self, t: float, text: str, meta=None):
        """Encode un texte et le stocke avec timestamp et métadonnées."""
        vec = self.encoder.encode(text)
        self.vectors.append((t, vec, meta))
        self.vectors = self.vectors[-self.max_length:]

    def query(self, text: str, top_k=5):
        """Interroge la mémoire par similarité vectorielle."""
        if not self.vectors:
            return []
        query_vec = self.encoder.encode(text)
        similarities = [(t, meta, np.dot(query_vec, v) / (np.linalg.norm(query_vec) * np.linalg.norm(v)))
                        for (t, v, meta) in self.vectors]
        similarities.sort(key=lambda x: x[2], reverse=True)
        return similarities[:top_k]

    def get_status(self):
        return {
            "module": self.name,
            "stored_vectors": len(self.vectors)
        }
