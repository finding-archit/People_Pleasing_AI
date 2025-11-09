# People Pleasing AI – Conflict Resolution

A modular, multi-agent conversational AI platform for actionable conflict resolution and compromise generation.  
Extracts perspectives, detects emotion and intent, generates nuanced compromise via LLMs, and enforces safety—all with a professional Streamlit UI and CLI pipeline.

---

## Features

- Stance/perspective, sentiment/intent, reconciliation, and safety agents as microservices (FastAPI)
- Modular Python architecture with orchestration script
- Full-featured live web UI (Streamlit) for user input, persona analysis, and feedback
- Markdown and CSV analytics, batch or interactive evaluation
- Easy-to-extend, research-ready design

---

## Quickstart

### 1. Clone and Install

git clone https://github.com/finding-archit/People_Pleasing_AI.git
cd People_Pleasing_AI
python -m venv .venv
.venv\Scripts\activate # On Windows
pip install -r requirements.txt

### 2. Start Pipeline Agents (New Terminal for Each)

uvicorn services.perspective.app:app --port 8001
uvicorn services.sentiment_intent.app:app --port 8002
uvicorn services.reconcile.app:app --port 8003
uvicorn services.safety.app:app --port 8004

### 3. Start UI

cd ui
streamlit run app.py

---

## Project Structure

orchestration/ # Main pipeline runner and results
services/
perspective/
sentiment_intent/
reconcile/
safety/
ui/ # Streamlit UI
data/ # (for local data, gitignored)
libs/ # (for models, gitignored)


---

## Usage

- Use the CLI pipeline via `orchestration/main.py` for batch/Bash output and CSV logging.
- For live user testing, use `ui/app.py` (Streamlit).
- Each microservice agent can be developed or replaced independently.

---

## Contributors

- Archit Gupta
- Rounaq Moin
- Gunda Rama Praneetha

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Notes

- Make sure `.venv/`, `libs/`, and all model/data binaries are **gitignored**.
- Use `pip freeze > requirements.txt` when updating dependencies.

---

*Optimized for research, collaboration, and real-world conversational AI.*  
