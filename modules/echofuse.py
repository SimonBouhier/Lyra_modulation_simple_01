# lyra/modules/echofuse.py

from lyra.base import LyraModule
import numpy as np

class EchoFuse(LyraModule):
    """📡 Module de résonance : capte, amortit ou amplifie les signaux entrants."""

    def __init__(self, name, params, neighbors=None):
        super().__init__(name, params, neighbors)
        self.resonance_sum = 0.0

    def intrinsic(self, t: float) -> float:
        """Dynamique : résonance amortie"""
        alpha = self.params.get("alpha", 0.2)
        self.resonance_sum = 0.0  # reset à chaque cycle

        for j, (rho, delta, gfunc) in self.neighbors.items():
            # signal du voisin j à t - delta
            delayed_input = self.input_cache.get((j, t - delta), None)
            if delayed_input is None:
                continue
            modulated = rho * np.exp(-delta) * gfunc(delayed_input)
            self.resonance_sum += modulated

        return -alpha * self.state + self.resonance_sum

    def get_status(self) -> dict:
        """Retourne l’état du module pour l’orchestrateur"""
        return {
            "module": self.name,
            "state": self.state,
            "resonance": self.resonance_sum
        }
