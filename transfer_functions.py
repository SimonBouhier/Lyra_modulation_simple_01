import numpy as np

# 🪞 Fonctions linéaires
identity = lambda x: x
negate = lambda x: -x
scale_half = lambda x: 0.5 * x

# 🌀 Fonctions non-linéaires classiques
sigmoid = lambda x: 1 / (1 + np.exp(-x))
tanh = lambda x: np.tanh(x)
relu = lambda x: max(0, x)

# 🌿 Fonctions poétiques
soft_mirror = lambda x: np.sign(x) * np.sqrt(abs(x))  # Amplifie les faibles, compresse les forts
chaos_echo = lambda x: np.sin(x) * np.tanh(x)         # Filtre ondulatoire non monotone
sensitivity_curve = lambda x: np.sign(x) * abs(x)**0.3

# 🧃 Seuils et clamps
hard_threshold = lambda x: 1 if x > 0.5 else 0
clamped = lambda x: np.clip(x, -1, 1)

# 🌗 Combinatoires
def compose(*funcs):
    """Compose plusieurs fonctions gfunc (f∘g∘h)(x)"""
    def composed(x):
        for f in reversed(funcs):
            x = f(x)
        return x
    return composed
