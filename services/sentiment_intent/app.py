from fastapi import FastAPI
from pydantic import BaseModel
from libs.common.schemas import SentimentsJSON, SentimentIntent #structures for outputting results neatly
from transformers import AutoTokenizer, AutoModelForSequenceClassification #loads goemotions rpberta model
import torch #for running interface smoothly

model_name = "SamLowe/roberta-base-go_emotions"
tokenizer = AutoTokenizer.from_pretrained(model_name) #text to tokens to numerical data
model = AutoModelForSequenceClassification.from_pretrained(model_name)

EMOTION_LABELS = [
    "admiration", "amusement", "anger", "annoyance", "approval", "caring",
    "confusion", "curiosity", "desire", "disappointment", "disapproval", "disgust",
    "embarrassment", "excitement", "fear", "gratitude", "grief", "joy", "love",
    "nervousness", "optimism", "pride", "realization", "relief", "remorse", "sadness",
    "surprise", "neutral"
]

app = FastAPI()

class UserPair(BaseModel): #statements of both users
    user_A_text: str
    user_B_text: str

def infer_emotions(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True) #tokenizzes and passes to goemotions - pytorch tensors
    with torch.no_grad(): #roberta model in pytorch foramt
        logits = model(**inputs).logits #number crunching
        probs = torch.sigmoid(logits)[0].cpu().numpy() #sigmoid function for multi label properties per emotion
    emotions = {lab: float(prob) for lab, prob in zip(EMOTION_LABELS, probs) if prob > 0.3} #confident emotions greater than 0.3 (dominant)
    top_intent = max(emotions, key=emotions.get, default="neutral") if emotions else "neutral"#emotion of highest score
    valence = float(probs[EMOTION_LABELS.index("joy")]) - float(probs[EMOTION_LABELS.index("anger")]) #joy scores - anger scores
    return emotions, top_intent, valence #things it returns

@app.post("/analyze", response_model=SentimentsJSON) #when called
def analyze(user_input: UserPair):
    emo_A, intent_A, val_A = infer_emotions(user_input.user_A_text) #runs extraction for both
    emo_B, intent_B, val_B = infer_emotions(user_input.user_B_text)
    sent_A = SentimentIntent(valence=val_A, emotion_scores=emo_A, intent=intent_A)
    sent_B = SentimentIntent(valence=val_B, emotion_scores=emo_B, intent=intent_B) #packages results as helper objects
    return SentimentsJSON(user_A_sentiment=sent_A, user_B_sentiment=sent_B) #used in other agents as
