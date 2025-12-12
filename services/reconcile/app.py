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

1. Infer a concise persona for User A and User B.
2. Then write one message to User A and one message to User B.

Format your final answer EXACTLY like this, in this order:

**User A Persona:**
<1–2 sentences about A’s motivations, values, and emotional state.>

**User B Persona:**
<1–2 sentences about B’s motivations, values, and emotional state.>

**Message to User A:**
<2–4 sentences, speaking to A as "you". Explain B’s perspective in A’s terms, ask A to sacrifice/soften at least one part of their stance, and tell A one important thing they should keep.>

**Message to User B:**
<2–4 sentences, speaking to B as "you". Explain A’s perspective in B’s terms, ask B to sacrifice/soften at least one part of their stance, and tell B one important thing they should keep.>

Rules:
- Keep total output under 180 words.
- Do not add any other headings, bullets, or text.
- Be firm, fair, and realistic—not overly sweet.


"""
    return prompt

def call_mistral_llm(prompt: str, model="mistral"): #request to locally running mistral
    r = requests.post(
        "http://localhost:11434/api/generate", #via ollama
        json={
            "model": model,
            "prompt": prompt,
            "stream": False #get the full ans in one go
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
