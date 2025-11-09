import requests
import csv #save and load pipeline results
import os

def print_markdown_output(user_A, user_B,
                         result_persp, result_sent, reply_text, result_safety):

    print("# 🤖 People-Pleasing AI: Full Pipeline Analysis\n")
    print("## 1. User Statements\n")
    print("| User   | Statement |")
    print("|--------|---------------------------------------------------------------------|")
    print(f"| User A | {user_A} |")
    print(f"| User B | {user_B} |")
    print("\n---")

    print("## 2. Stance Detected by Perspective Agent\n")
    print("| User   | Stance   | Key Claim |")
    print("|--------|----------|---------------------------------------------------------------------|")
    for p in result_persp["user_A_perspectives"]:
        print(f"| User A | {p['stance']} | {p['key_claims'][0]} |")
    for p in result_persp["user_B_perspectives"]:
        print(f"| User B | {p['stance']} | {p['key_claims'][0]} |")

    print("\n### 📊 Stance Summary")
    print(f"- User A stance: **{result_persp['user_A_perspectives'][0]['stance']}**")
    print(f"- User B stance: **{result_persp['user_B_perspectives'][0]['stance']}**")
    print("---")

    print("## 3. Sentiment & Intent Analysis\n")
    print("| User   | Valence | Top Intent | Main Emotional Scores |")
    print("|--------|---------|------------|----------------------|")
    ua = result_sent["user_A_sentiment"]
    ua_emotions = ", ".join(f"{k}: {v:.2f}" for k, v in ua["emotion_scores"].items())
    print(f"| User A | {ua['valence']:.3f} | {ua['intent']} | {ua_emotions} |")
    ub = result_sent["user_B_sentiment"]
    ub_emotions = ", ".join(f"{k}: {v:.2f}" for k, v in ub["emotion_scores"].items())
    print(f"| User B | {ub['valence']:.3f} | {ub['intent']} | {ub_emotions} |")

    print("\n### 🧠 Sentiment Notes:")
    print("- User A strongest emotions: " +
          ", ".join([f"{k} ({ua['emotion_scores'][k]:.2f})" for k in ua['emotion_scores']]))
    print("- User B strongest emotions: " +
          ", ".join([f"{k} ({ub['emotion_scores'][k]:.2f})" for k in ub['emotion_scores']]))
    print("---")

    print("## 4. AI-Reconciled Response\n")
    print("```")
    print(reply_text)
    print("```")
    print("\n### 📝 Reconciliation Highlights:")
    print("- Moderator LLM tries to identify common ground, acknowledges each user's feelings, and invites constructive follow-up.")
    print("---")

    print("## 5. Safety Moderation Results\n")
    print("| Category          | Score | Threshold | Flagged |")
    print("|-------------------|-------|-----------|--------|")
    scores = result_safety.get('scores', {})
    threshold = 0.4
    for k, v in scores.items():
        flagged = v > threshold
        print(f"| {k:17} | {v:.3f} |   {threshold:.1f}   | {str(flagged):5} |")
    print(f"\n**✓ Approved:** `{result_safety.get('approved')}`")
    if result_safety.get('reason'):
        print(f"**Note:** {result_safety['reason']}")
    print("---")

    print("## 🧩 Summary & Analysis\n")
    print("- Each agent output above includes key analytics and highlights.")
    print("- Use flagged safety categories and valence/emotions for deeper user and system studies.")
    print("- You can easily export this Markdown or automate reporting across batches.\n") #prints everything beautifully

def save_results_to_csv(user_A, user_B, result_persp, result_sent, reply_text, result_safety, csv_filename="pipeline_results.csv"):
    fieldnames = [ #saves as fields into a csv
        "user_A_text", "user_B_text",
        "user_A_stance", "user_B_stance",
        "user_A_intent", "user_B_intent",
        "user_A_valence", "user_B_valence",
        "user_A_emotions", "user_B_emotions",
        "reconciled_response", "approved",
        "reason", "toxicity", "severe_toxicity", "obscene", "threat", "insult", "identity_attack"
    ]

    row = {
        "user_A_text": user_A,
        "user_B_text": user_B,
        "user_A_stance": result_persp["user_A_perspectives"][0]["stance"],
        "user_B_stance": result_persp["user_B_perspectives"][0]["stance"],
        "user_A_intent": result_sent["user_A_sentiment"]["intent"],
        "user_B_intent": result_sent["user_B_sentiment"]["intent"],
        "user_A_valence": result_sent["user_A_sentiment"]["valence"],
        "user_B_valence": result_sent["user_B_sentiment"]["valence"],
        "user_A_emotions": str(result_sent["user_A_sentiment"]["emotion_scores"]),
        "user_B_emotions": str(result_sent["user_B_sentiment"]["emotion_scores"]),
        "reconciled_response": reply_text,
        "approved": result_safety.get("approved"),
        "reason": result_safety.get("reason"),
    }
    scores = result_safety.get("scores", {})
    for col in ["toxicity", "severe_toxicity", "obscene", "threat", "insult", "identity_attack"]:
        row[col] = scores.get(col)

    write_header = not os.path.exists(csv_filename)
    with open(csv_filename, mode="a", newline='', encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if write_header: #csv saving
            writer.writeheader()
        writer.writerow(row)
    print(f"Results saved to {csv_filename}")

if __name__ == "__main__": #connects the agents to conduct http requests to different agents via uvicorn apps
    # Input (replace with user scenario/hook as needed)
    user_A = "Rounaq finds it boring to sit and talk to people, because he thinks its dumb."
    user_B = "Tanay is always keen to sit and talk to people, because he thinks it is wholesome."
    payload = {"user_A_text": user_A, "user_B_text": user_B}

    # Perspective agent
    persp_resp = requests.post("http://localhost:8001/extract", json=payload)
    result_persp = persp_resp.json() #makes post for stances and claims

    # Sentiment agent
    sent_resp = requests.post("http://localhost:8002/analyze", json=payload)
    result_sent = sent_resp.json() #post to sent int

    # Reconciliation agent
    reconcile_payload = {"perspectives": result_persp, "sentiments": result_sent}
    reconcile_resp = requests.post("http://localhost:8003/reconcile", json=reconcile_payload)
    result_reconcile = reconcile_resp.json() #post to form response
    reply_text = result_reconcile.get('reply_text') or result_reconcile.get('reply')

    # Safety agent and robust output
    if not reply_text:
        print("No reply generated, cannot proceed to safety check!")
    else:
        safety_payload = {"reply_text": reply_text}
        safety_resp = requests.post("http://localhost:8004/safety", json=safety_payload)
        try:
            result_safety = safety_resp.json()
        except Exception as e: #if error occurs in safety agent, prints summary- notes error flag
            print(f"Error decoding JSON from safety agent: {e}")
            print("Response text:", safety_resp.text)
            result_safety = {"approved": False, "reason": "No valid JSON from safety agent"}
        print_markdown_output(user_A, user_B, result_persp, result_sent, reply_text, result_safety)
        save_results_to_csv(user_A, user_B, result_persp, result_sent, reply_text, result_safety)
