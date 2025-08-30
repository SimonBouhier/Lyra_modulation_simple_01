"""FastAPI pour exposer LyraCoreMinimal via HTTP.

Endpoints :
    • POST /lyra  {"prompt": str}  → réponse stylisée + états internes
    • GET  /status                 → horodatage, nombre de traces, alertes CRITRIX
    • POST /reset                 → réinitialise le core (facultatif)

L’application charge un unique LyraCoreMinimal en mémoire.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime

from lyra.core_pipeline import LyraCoreMinimal

app = FastAPI(title="Lyra API", version="0.1")
core = LyraCoreMinimal(dt=0.1)

class PromptIn(BaseModel):
    prompt: str

@app.post("/lyra")
async def run_lyra(data: PromptIn):
    if len(data.prompt.strip()) == 0:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    result = core.step(user_prompt=data.prompt)
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "styled_output": result["styled_output"],
        "critrix_alert": result["critrix_alert"],
        "noyau_state": result["noyau_state"],
        "t": result["t"],
    }

@app.get("/status")
async def status():
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "t": round(core.t, 2),
        "memory_traces": core.journal.get_status()["active_traces"],
        "critrix_alert": core.critrix.is_over_threshold,
    }

@app.post("/reset")
async def reset_core():
    global core
    core = LyraCoreMinimal(dt=0.1)
    return {"status": "reset", "timestamp": datetime.utcnow().isoformat()}

# Pour exécuter :
#   uvicorn lyra.api:app --reload
