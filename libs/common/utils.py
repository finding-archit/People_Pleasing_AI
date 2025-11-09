import uuid
def generate_request_id():
    return str(uuid.uuid4())

def log(msg):
    print(f"[LOG] {msg}")
