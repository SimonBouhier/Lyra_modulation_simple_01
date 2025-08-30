# lyra/modules/llm_bridge.py
"""AutoGenesisCoreLLM – passerelle OpenAI pour Lyra.

- Charge la clé via variable d'environnement `OPENAI_API_KEY` ou via `lyra.config.OPENAI_API_KEY`.
- Utilise `OPENAI_MODEL` comme modèle par défaut (configurable).
- Convertit la longueur (tokens) de la réponse en un signal numérique `state` ∈ [0, 1].
  (simple mais suffisant pour pilotage initial ; pourra être raffiné plus tard.)
- Aucune dépendance circulaire.
"""

import os, openai
from lyra.base import LyraModule
from lyra.config import OPENAI_API_KEY, OPENAI_MODEL

# Initialise la clé – priorité à la variable d'environnement (plus sûre)
openai.api_key = os.getenv("OPENAI_API_KEY", OPENAI_API_KEY)

class AutoGenesisCoreLLM(LyraModule):
    """Module génératif branché sur l'API OpenAI."""

    def __init__(self, name: str, params: dict | None = None, neighbors: dict | None = None):
        params = params or {}
        super().__init__(name, params, neighbors)
        self.model = params.get("model", OPENAI_MODEL)
        self.last_text: str = ""

    # ------------------------------------------------------------------
    def intrinsic(self, t: float) -> float:
        """Pas de dynamique interne continue : état mis à jour par prompt_llm."""
        return 0.0

    # ------------------------------------------------------------------
    def prompt_llm(self, user_prompt: str):
        """Interroge le modèle OpenAI, met à jour self.state.

        `state` est mappé sur [0,1] via len(text)/max_len.
        """
        user_prompt = user_prompt.strip()
        if not user_prompt:
            return

        try:
            resp = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": user_prompt}],
                temperature=0.8,
                max_tokens=150,
            )
        except openai.error.OpenAIError as exc:
            # logge l'erreur ; garde l'état précédent
            self.last_text = f"[OpenAIError] {exc}"
            return

        self.last_text = resp.choices[0].message.content.strip()

        # mapping : amplitude proportionnelle à la longueur (soft capped)
        self.state = min(len(self.last_text) / 200.0, 1.0)

    # ------------------------------------------------------------------
    def get_last_text(self) -> str:
        return self.last_text
