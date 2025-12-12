import subprocess
import sys
import os

BASE_DIR = r"D:\people_pleasing_ai"
VENV_PY = os.path.join(BASE_DIR, ".venv", "Scripts", "python.exe")

def run(cmd, cwd=None):
    return subprocess.Popen(cmd, cwd=cwd, creationflags=subprocess.CREATE_NEW_CONSOLE)

def main():
    # 1) Perspective
    run([VENV_PY, "-m", "uvicorn", "services.perspective.app:app", "--port", "8001"], cwd=BASE_DIR)

    # 2) Sentiment/Intent
    run([VENV_PY, "-m", "uvicorn", "services.sentiment_intent.app:app", "--port", "8002"], cwd=BASE_DIR)

    # 3) Reconcile
    run([VENV_PY, "-m", "uvicorn", "services.reconcile.app:app", "--port", "8003"], cwd=BASE_DIR)

    # 4) Safety
    run([VENV_PY, "-m", "uvicorn", "services.safety.app:app", "--port", "8004"], cwd=BASE_DIR)

    # 5) Orchestrator (optional)
    #run([VENV_PY, "orchestration\\main.py"], cwd=BASE_DIR)

    # 6) Streamlit UI
    run([VENV_PY, "-m", "streamlit", "run", "app.py"], cwd=os.path.join(BASE_DIR, "ui"))

if __name__ == "__main__":
    main()
