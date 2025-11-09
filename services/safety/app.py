from fastapi import FastAPI
from pydantic import BaseModel
from detoxify import Detoxify #pretrained model to score text on various kinda oh harm, toxicity, threat

app = FastAPI()
detox_model = Detoxify('original')
#toxicity, obscene, identity attack, insult, threat scoring from 0 to 1
class SafetyInput(BaseModel):
    reply_text: str #only input to this field is the response generated

@app.post("/safety") #if called
def check_safety(data: SafetyInput):
    try:
        results = detox_model.predict(data.reply_text) #predicts values
        # Explicitly convert all numpy floats to Python native floats:
        results_py = {k: float(v) for k, v in results.items()}
        flagged = {k: v for k, v in results_py.items() if v > 0.4} #flagged if 0.4
        approved = not bool(flagged)
        reason = f"Flagged scores: {flagged}" if flagged else None
        return { 
            "approved": approved,#true if no category is flagged
            "reason": reason,
            "scores": results_py # returns raw scores, flag and reason
        }
    except Exception as e:
        print("DETOXIFY ERROR:", str(e)) 
        return { #in case of error or failing
            "approved": False,
            "reason": f"Detoxify failed: {str(e)}",
            "scores": {}
        }
