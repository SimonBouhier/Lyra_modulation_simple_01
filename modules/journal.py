# lyra/modules/journal.py

from lyra.base import LyraModule
from sentence_transformers import SentenceTransformer
import numpy as np

class JournalOubli(LyraModule):
    """📜 JournalOubli — Mémoire filtrante à évaporation contrôlée avec traces vectorielles.

    • Chaque signal stocke : (timestamp, value, vector, meta)
    • Double indexation : texte lisible (meta['text_form']) + vecteur
    • Le vecteur reste auxiliaire : aucune logique centrale ne dépend de la similarité
    """

    def __init__(self, name, params, neighbors=None):
        super().__init__(name, params, neighbors)
        self.memory = []  # [(timestamp, value, vector, meta)]
        self.decay_lambda = self.params.get("lambda", 0.5)
        self.threshold = self.params.get("threshold", 0.01)
        self.max_length = self.params.get("max_length", 100)
        self.encoder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    # ---------------------------------------------------------------------
    # Dynamiques principales
    # ---------------------------------------------------------------------
    def intrinsic(self, t: float) -> float:
        return 0.0  # pas de dynamique interne propre

    def step(self, t: float, ext_inputs: dict) -> float:
        """Met à jour la mémoire (décroissance + capture de nouveaux signaux)."""
        # 1. Décroissance exponentielle
        decayed = []
        for timestamp, value, vector, meta in self.memory:
            age = t - timestamp
            new_value = value * np.exp(-self.decay_lambda * age)
            if abs(new_value) > self.threshold:
                decayed.append((timestamp, new_value, vector, meta))
        self.memory = decayed[-self.max_length:]

        # 2. Capture des signaux entrants depuis les voisins
        for j, (rho, delta, gfunc) in self.neighbors.items():
            if j not in ext_inputs:
                continue
            delayed_input = ext_inputs[j](t - delta)
            signal = rho * gfunc(delayed_input)
            if abs(signal) > self.threshold:
                text_form = f"{self.name}:{j}:{signal:.3f}"
                vector = self.encoder.encode(text_form)
                meta = {"source": j, "text_form": text_form}
                self.memory.append((t, signal, vector, meta))

        self.state = sum(v for (_, v, _, _) in self.memory)
        return self.state

    # ---------------------------------------------------------------------
    # Interfaces externes
    # ---------------------------------------------------------------------
    def remember(self, n: int = 5):
        """Retourne les n dernières traces non oubliées."""
        return self.memory[-n:]

    def query_similar(self, text: str, top_k: int = 5):
        """Renvoie les souvenirs vectoriellement proches d'un texte.

        • Ne modifie aucune décision interne.
        • Utilise une similarité cosinus simple (0..1).
        • Retour : [(timestamp, value, meta, score)] triés décroissant.
        """
        if not self.memory:
            return []
        q_vec = self.encoder.encode(text)
        if np.linalg.norm(q_vec) == 0:
            return []
        sims = []
        for timestamp, value, vec, meta in self.memory:
            denom = (np.linalg.norm(q_vec) * np.linalg.norm(vec)) or 1e-8
            score = float(np.dot(q_vec, vec) / denom)
            sims.append((timestamp, value, meta, score))
        sims.sort(key=lambda x: x[3], reverse=True)
        return sims[:top_k]

    def get_status(self):
        return {
            "module": self.name,
            "active_traces": len(self.memory),
            "state": self.state
        }
