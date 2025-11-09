from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any
import requests # to contact mistral

app = FastAPI()

class ReconcileContext(BaseModel):
    perspectives: Dict[str, Any]
    sentiments: Dict[str, Any]

def compose_prompt(ctx: ReconcileContext): #construct and loads into prompt
    ua_stance = ctx.perspectives['user_A_perspectives'][0]['stance']
    ub_stance = ctx.perspectives['user_B_perspectives'][0]['stance']
    ua_claim = ctx.perspectives['user_A_perspectives'][0]['key_claims'][0]
    ub_claim = ctx.perspectives['user_B_perspectives'][0]['key_claims'][0]
    ua_emotion = ctx.sentiments['user_A_sentiment']['intent']
    ub_emotion = ctx.sentiments['user_B_sentiment']['intent']
    ua_valence = ctx.sentiments['user_A_sentiment']['valence']
    ub_valence = ctx.sentiments['user_B_sentiment']['valence']

    prompt = f""" 
**User A:**
- Perspective: "{ua_claim}"
- Stance: {ua_stance}
- Intent/Emotion: {ua_emotion}
- Valence: {ua_valence:.2f}

**User B:**
- Perspective: "{ub_claim}"
- Stance: {ub_stance}
- Intent/Emotion: {ub_emotion}
- Valence: {ub_valence:.2f}

---

Your task:
1. Frame each user's persona based on their sentiment, intent, stance, and valence above. Be direct and realistic about their emotional state and motivations.
2. Acknowledge both viewpoints, explaining the justification and reasoning behind each user's position.
3. Propose a single balanced response that sheds light on each perspective, highlighting where compromise is necessary.
4. Do not sugarcoat or be excessively kind—be firm, fair, and direct. Use straightforward language.
5. Keep your entire response to 100 words or fewer.

Focus on actionable outcomes and necessary trade-offs, not empty reassurances.
"""
    return prompt

def call_mistral_llm(prompt: str, model="mistral"): #request to locally running mistral
    r = requests.post(
        "http://localhost:11434/api/generate", #via ollama
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        }
    )
    r.raise_for_status()
    output = r.json() #response as output
    return output['response'] if 'response' in output else output.get('text', '')

@app.post("/reconcile") #if called
def reconcile(ctx: ReconcileContext):
    prompt = compose_prompt(ctx)
    reply = call_mistral_llm(prompt)
    return {"reply": reply}
