import os
import json
from datetime import datetime

def log_interaction_json(thinker_key, question, answer):
    os.makedirs("logs", exist_ok=True)
    filepath = os.path.join("logs", "interaction_log.json")

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "thinker": thinker_key,
        "question": question,
        "answer": answer
    }

    with open(filepath, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
