# lyra/modules/critrix.py

from lyra.base import LyraModule
import numpy as np

class CRITRIX(LyraModule):
    """🧃 Module critique dialectique : détecte les tensions excessives tout en évaluant leur valeur poétique."""

    def __init__(self, name, params, neighbors=None):
        super().__init__(name, params, neighbors)
        self.is_over_threshold = False
        self.coherence_score = 1.0
        self.last_output = 0.0

    def intrinsic(self, t: float) -> float:
        tau_in = self.params.get("tau_in", 0.0)
        theta_C = self.params.get("theta_C", 1.0)
        gamma = self.params.get("gamma", 1.0)
        eta_C = self.params.get("eta_C", 0.2)

        excitation = gamma * max(0, tau_in - theta_C)
        dissipation = eta_C * self.tau_c
        d_tau_c = excitation - dissipation

        self.tau_c += d_tau_c * self.params.get("dt", 0.1)
        self.tau_c = np.clip(self.tau_c, 0.0, 10.0)

        self.coherence_score = 1.0 / (1.0 + abs(tau_in - self.tau_c))
        self.is_over_threshold = (self.tau_c > theta_C and self.coherence_score < 0.4)

        self.last_output = -self.tau_c  # valeur utilisée par d'autres modules

        return self.last_output

    def inject_tau_in(self, value: float):
        self.params["tau_in"] = value

    def get_status(self) -> dict:
        """Expose l’état interne pour les modules régulateurs (SilenceØ, LYRA_CORE, etc.)"""
        return {
            "module": self.name,
            "output": self.last_output,
            "tau_c": self.tau_c,
            "coherence": self.coherence_score,
            "alert": self.is_over_threshold
        }
