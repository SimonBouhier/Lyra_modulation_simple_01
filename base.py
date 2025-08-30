from abc import ABC, abstractmethod
import numpy as np
from typing import Dict, Callable, Tuple


class LyraModule(ABC):
    """🌱 Un module de Lyra, une spore vibrante tissant des dynamiques organiques.

    Attributes:
        name (str): Nom du module, une empreinte dans le réseau mycélien.
        state (float): État courant, une pulsation du module.
        params (dict): Paramètres, les racines de la dynamique.
        neighbors (dict): Voisins {name: (rho, delta, gfunc)}, filaments de couplage.
        tau_c (float): Tension locale, écho de la cohérence critique.
    """

    def __init__(self, name: str, params: Dict, neighbors: Dict[str, Tuple[float, float, Callable]] = None):
        if not isinstance(name, str) or not name:
            raise ValueError("Name must be a non-empty string")
        if not isinstance(params, dict):
            raise ValueError("Params must be a dictionary")
        self.name = name
        self.state = params.get("state0", 0.0)
        self.params = params
        self.neighbors = neighbors or {}
        self.input_cache = {}
        self.tau_c = 0.0
        self._validate_neighbors()

    def _validate_neighbors(self):
        for j, (rho, delta, gfunc) in self.neighbors.items():
            if not isinstance(rho, (int, float)) or not isinstance(delta, (int, float)):
                raise ValueError(f"Invalid rho or delta for neighbor {j}")
            if not callable(gfunc):
                raise ValueError(f"gfunc for neighbor {j} must be callable")

    def add_neighbor(self, name: str, rho: float, delta: float, gfunc: Callable[[float], float]):
        """Ajoute un voisin, un filament mycélien."""
        self.neighbors[name] = (rho, delta, gfunc)
        self._validate_neighbors()

    def update_tau_c(self, input_value: float, output_value: float) -> float:
        """Calcule la tension locale, écho de la cohérence."""
        self.tau_c = abs(input_value - output_value) / (abs(input_value) + 1e-10)
        return self.tau_c

    @abstractmethod
    def intrinsic(self, t: float) -> float:
        """Dynamique propre du module, son souffle intérieur."""
        pass

    def step(self, t: float, ext_inputs: Dict[str, Callable[[float], float]]) -> float:
        """Évolue l’état, tissant les influences internes et externes."""
        if not isinstance(ext_inputs, dict):
            raise ValueError("ext_inputs must be a dictionary of callables")
        dx = self.intrinsic(t)
        for j, (rho, delta, gfunc) in self.neighbors.items():
            if j not in ext_inputs:
                continue
            cache_key = (j, t - delta)
            if cache_key not in self.input_cache:
                self.input_cache[cache_key] = ext_inputs[j](t - delta)
            input_value = self.input_cache[cache_key]
            dx += rho * gfunc(input_value)
        self.state += dx * self.params.get("dt", 0.1)
        self.state = np.clip(self.state, -10, 10)
        return self.state


# 🔬 Exemple minimal de module lyrique
class PoeticModule(LyraModule):
    """Un module poétique, tissant des pulsations créatives."""
    def intrinsic(self, t: float) -> float:
        return -self.params.get("alpha", 0.1) * self.state + np.sin(t)


# 🧪 Test local
if __name__ == "__main__":
    def identity(x): return x

    module1 = PoeticModule("metaphor", {"state0": 1.0, "alpha": 0.2, "dt": 0.1})
    module2 = PoeticModule("pun", {"state0": 0.5, "alpha": 0.15, "dt": 0.1})

    module1.add_neighbor("pun", rho=0.5, delta=0.1, gfunc=identity)
    module2.add_neighbor("metaphor", rho=0.3, delta=0.2, gfunc=identity)

    ext_inputs = {
        "metaphor": lambda t: module1.state,
        "pun": lambda t: module2.state
    }

    for t in np.arange(0, 10, 0.1):
        s1 = module1.step(t, ext_inputs)
        s2 = module2.step(t, ext_inputs)
        print(f"t={t:.1f}, metaphor={s1:.2f}, pun={s2:.2f}")
