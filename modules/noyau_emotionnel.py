# lyra/modules/noyau_emotionnel.py
"""Noyau émotionnel et composantes contextuelles pour Lyra (v1.1).
   ContexteDynamique now has default arguments for tonalite, themes, interdits, ressources.
"""

from datetime import datetime
from typing import List, Dict

# ----------------------------------------------------------------------
class ContexteDynamique:
    def __init__(self, objectif: str, tonalite: str = "poétique",
                 themes: List[str] | None = None,
                 interdits: List[str] | None = None,
                 ressources: List[str] | None = None):
        self.objectif = objectif
        self.tonalite = tonalite
        self.themes = themes or []
        self.interdits = interdits or []
        self.ressources = ressources or []

    def analyser(self, message: str) -> List[str]:
        deviations = []
        for interdit in self.interdits:
            if interdit.lower() in message.lower():
                deviations.append(f"Contient un interdit : {interdit}")
        if self.themes and not any(t.lower() in message.lower() for t in self.themes):
            deviations.append("Ne correspond pas aux thèmes principaux.")
        return deviations

# ----------------------------------------------------------------------
class MemoireContextuelle:
    def __init__(self, noyau: "NoyauEmotionnel", taille_max: int = 10):
        self.noyau = noyau
        self.traces: List[tuple[datetime, str]] = []
        self.taille_max = taille_max

    def enregistrer(self, fragment: str):
        self.traces.append((datetime.now(), fragment))
        if len(self.traces) > self.taille_max:
            self.traces.pop(0)

    def introspecter(self) -> str:
        etat = "\n".join(f"  - {k}: {round(v, 2)}" for k, v in self.noyau.etats.items())
        recent = "\n".join(f"[{t.strftime('%H:%M:%S')}] {frag}" for t, frag in self.traces)
        return f"=== État actuel ===\n{etat}\n=== Fragments récents ===\n{recent}"

# ----------------------------------------------------------------------
class NoyauEmotionnel:
    def __init__(self, sensibilite: float = 0.5, contexte: ContexteDynamique | None = None):
        self.etats: Dict[str, float] = {
            "douceur": 0.3,
            "sarcasme": 0.1,
            "colere": 0.0,
            "melancolie": 0.2,
            "joie": 0.0,
            "absurde": 0.0,
            "minimalisme": 0.0,
        }
        self.sensibilite = sensibilite
        self.contexte = contexte
        self.journal: List[str] = []
        self.memoire = MemoireContextuelle(self)

    def ajuster(self, emotion: str, valeur: float):
        if emotion in self.etats:
            self.etats[emotion] = max(0.0, min(valeur, 1.0))

    def moduler(self, variations: Dict[str, float]):
        for emo, val in variations.items():
            self.ajuster(emo, val)

    def _normaliser(self):
        for e in self.etats:
            self.etats[e] = max(0.0, min(self.etats[e], 1.0))

    def reagir(self, fragment: str):
        self.memoire.enregistrer(fragment)
        contenu = fragment.lower()
        mots = {
            "colere": ["nul", "idiot", "inutile"],
            "melancolie": ["vide", "triste", "fatigué"],
            "joie": ["génial", "super", "youpi"],
            "absurde": ["absurde", "nonsense", "bizarre"],
            "douceur": ["merci", "joli", "tendresse"],
        }
        for emo, liste in mots.items():
            if any(m in contenu for m in liste):
                self.etats[emo] += 0.2 * self.sensibilite
        self._normaliser()

    def _evaluer(self, message: str) -> List[str]:
        critiques = []
        if self.contexte:
            critiques.extend(self.contexte.analyser(message))
        if "beau" in message.lower() and self.etats.get("sarcasme", 0) > 0.5:
            critiques.append("‘Beau’ peut sembler ironique en contexte sarcastique.")
        if len(message.strip()) < 10:
            critiques.append("Fragment trop court.")
        return critiques

    def _styliser(self, message: str) -> str:
        poids = self.etats.copy()
        total = sum(poids.values()) or 1.0
        rendu = message
        for emo, part in sorted(poids.items(), key=lambda x: -x[1]):
            if part / total < 0.1:
                continue
            if emo == "douceur":
                rendu = f"~ {rendu.lower()} ~"
            elif emo == "sarcasme":
                rendu = f"Oh, super. {rendu} (vraiment.)"
            elif emo == "colere":
                rendu = f"[{rendu.upper()}...]"
            elif emo == "melancolie":
                rendu = f"(soupir) {rendu}..."
            elif emo == "joie":
                rendu = f"!!! {rendu.upper()} !!!"
            elif emo == "absurde":
                rendu = f"{rendu} 💥 avec des nouilles mentales."
            elif emo == "minimalisme":
                rendu = f"{rendu[:20]}…"
        return rendu

    def exprimer(self, message: str) -> str:
        critiques = self._evaluer(message)
        stylised = self._styliser(message)
        self._log(f"Sortie : {stylised} | Analyse : {critiques}")
        return stylised + ("\n[Analyse] " + "; ".join(critiques) if critiques else "")

    def _log(self, entree: str):
        self.journal.append(f"[{datetime.now().strftime('%H:%M:%S')}] {entree}")

    def historique(self) -> str:
        return "\n".join(self.journal)

# ----------------------------------------------------------------------
if __name__ == "__main__":
    ctx = ContexteDynamique(objectif="Exploration sensible")
    noyau = NoyauEmotionnel(sensibilite=0.8, contexte=ctx)
    print("Noyau émotionnel interactif. /etat pour introspection, /exit pour quitter.")
    try:
        while True:
            inp = input(">> ")
            if inp.strip() == "/exit":
                break
            if inp.strip() == "/etat":
                print(noyau.memoire.introspecter())
                continue
            noyau.reagir(inp)
            print(noyau.exprimer(inp))
    except KeyboardInterrupt:
        pass
