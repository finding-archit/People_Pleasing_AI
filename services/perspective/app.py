from fastapi import FastAPI
from pydantic import BaseModel
from libs.common.schemas import PerspectivesJSON, Perspective
from transformers import pipeline

stance_pipeline = pipeline( #transformers pipeline for loading huggingface data
    task="text-classification",
    model="eevvgg/StanceBERTa",
    tokenizer="eevvgg/StanceBERTa"
)
label_map = {
    "positive": "support",
    "negative": "oppose",
    "neutral": "neutral"
}

app = FastAPI() #fast api ka backend

class UserPair(BaseModel): #inputs dono
    user_A_text: str
    user_B_text: str

def get_stance(text, actor):
    result = stance_pipeline(text)[0] #runs and takes the top prediction
    stance = label_map.get(result['label'].lower(), "neutral") #maps the label
    return Perspective( #extracts stance
        actor=actor,
        stance=stance,
        key_claims=[text]
    )

@app.post("/extract", response_model=PerspectivesJSON)
def extract(user_input: UserPair):
    persp_A = get_stance(user_input.user_A_text, "user_A")
    persp_B = get_stance(user_input.user_B_text, "user_B")
    return PerspectivesJSON(
        user_A_perspectives=[persp_A], #when agent called, fucntion lloads the user inputs into the model, sends to extract perspective.
        user_B_perspectives=[persp_B]
    )
