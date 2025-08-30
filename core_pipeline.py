"""Flux Lyra complet (v1.3)

Chaîne : AutoGenesisCoreLLM → JournalOubli → CRITRIX → EchoFuse
          + NoyauEmotionnel

Nouveauté  v1.3
----------------
•  La réponse **texte** du LLM est renvoyée sous la clé `reply`.
•  `styled_output` contient cette même réponse passée à la couche émotionnelle.
•  `critrix_alert` casté en `bool` natif (JSON‑safe).
"""

import os
from typing import Dict, Callable

from lyra.modules.llm_bridge import AutoGenesisCoreLLM
from lyra.modules.journal import JournalOubli
from lyra.modules.critrix import CRITRIX
from lyra.modules.echofuse import EchoFuse
from lyra.transfer_functions import identity, sigmoid
from lyra.modules.noyau_emotionnel import NoyauEmotionnel, ContexteDynamique


class LyraCoreMinimal:
    """Orchestrateur principal utilisé par l'API FastAPI."""

    def __init__(self, dt: float = 0.1):
        self.t = 0.0
        self.dt = dt

        # -------- Noyau émotionnel --------
        ctx = ContexteDynamique(objectif="Exploration sensible")
        self.noyau = NoyauEmotionnel(sensibilite=0.8, contexte=ctx)

        # -------- Modules primaires --------
        self.autogenesis = AutoGenesisCoreLLM(
            "autogenesis",
            {"model": os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"), "dt": dt},
        )

        self.journal = JournalOubli("journal", {"lambda": 0.4, "threshold": 0.01, "dt": dt})
        self.journal.add_neighbor("autogenesis", rho=1.0, delta=0.0, gfunc=identity)

        self.critrix = CRITRIX("critrix", {"theta_C": 0.8, "gamma": 1.2, "eta_C": 0.3, "dt": dt})

        self.echo = EchoFuse("echo", {"alpha": 0.2, "dt": dt})
        self.echo.add_neighbor("autogenesis", rho=0.6, delta=0.0, gfunc=sigmoid)

        self.modules = {
            "autogenesis": self.autogenesis,
            "journal": self.journal,
            "critrix": self.critrix,
            "echo": self.echo,
        }

    # ---------------------------------------------------------
    def _ext_inputs(self) -> Dict[str, Callable[[float], float]]:
        """Mapping name → callable(t) donnant l'état au temps t‑δ."""
        return {name: (lambda t, m=mod: m.state) for name, mod in self.modules.items()}

    # ---------------------------------------------------------
    def step(self, user_prompt: str = "") -> Dict:
        """Avance la simulation d'un pas et renvoie un dict JSON‑safe."""

        # 1) Réaction émotionnelle et génération LLM
        if user_prompt:
            self.noyau.reagir(user_prompt)
            self.autogenesis.prompt_llm(user_prompt)

        # 2) Mise à jour des modules
        self.journal.step(self.t, self._ext_inputs())
        self.critrix.inject_tau_in(abs(self.autogenesis.state))
        self.critrix.step(self.t, self._ext_inputs())

        if user_prompt:
            sim = self.journal.query_similar(user_prompt, top_k=1)
            if sim:
                _t0, val, meta, score = sim[0]
                self.echo.add_neighbor("journal", rho=score, delta=0.0, gfunc=identity)

        self.echo.step(self.t, self._ext_inputs())

        # 3) Construction de la réponse
        llm_text = self.autogenesis.get_last_text() or "(silence)"
        styled_text = self.noyau.exprimer(llm_text)

        # 4) Avance du temps
        self.t += self.dt

        return {
            "timestamp": self._iso_now(),
            "reply": llm_text,
            "styled_output": styled_text,
            "critrix_alert": bool(self.critrix.is_over_threshold),
            "noyau_state": self.noyau.etats.copy(),
            "t": round(self.t, 2),
        }

    # ---------------------------------------------------------
    @staticmethod
    def _iso_now():
        from datetime import datetime
        return datetime.utcnow().isoformat()


# ---------------------- Démo CLI ---------------------------
if __name__ == "__main__":
    core = LyraCoreMinimal(dt=0.25)
    print("Lyra CLI – Ctrl+C pour quitter")
    try:
        while True:
            p = input(">> ")
            if not p:
                continue
            res = core.step(p)
            print(res["styled_output"])
    except KeyboardInterrupt:
        print("\nBye.")
