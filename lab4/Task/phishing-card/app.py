from flask import Flask, render_template, request
from datetime import datetime
import os, json, re

app = Flask(__name__)

LOG_PATH = os.path.join("logs", "events.jsonl")
os.makedirs("logs", exist_ok=True)
if not os.path.exists(LOG_PATH):
    open(LOG_PATH, "w").close()

# Published test card numbers that are OK to use in training
ALLOWED_TEST_NUMS = {
    "4242424242424242",  # common Visa test
    "4111111111111111",  # Visa test
}

def log_event(evt: dict):
    evt["ts"] = datetime.utcnow().isoformat() + "Z"
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(evt, ensure_ascii=False) + "\n")

def digits_only(s: str) -> str:
    return re.sub(r"\D", "", s or "")

def luhn_ok(num: str) -> bool:
    total, alt = 0, False
    for ch in reversed(num):
        n = ord(ch) - 48
        if alt:
            n *= 2
            if n > 9:
                n -= 9
        total += n
        alt = not alt
    return total % 10 == 0

def looks_like_real_pan(num: str) -> bool:
    if num in ALLOWED_TEST_NUMS:
        return False
    return 13 <= len(num) <= 19 and luhn_ok(num)

@app.get("/")
def index():
    return render_template("index.html", message=None, message_type=None)

@app.post("/submit")
def submit():
    # Read form fields (never store them)
    name = (request.form.get("name") or "").strip()
    number = digits_only(request.form.get("number"))
    exp = (request.form.get("exp") or "").strip()
    cvv = digits_only(request.form.get("cvv"))

    # Server-side checks: block anything that *resembles* real secrets
    attempted_sensitive = False
    if looks_like_real_pan(number):
        attempted_sensitive = True
    if 3 <= len(cvv) <= 4:
        attempted_sensitive = True
    if re.match(r"^\d{2}\s*/\s*\d{2,4}$", exp or ""):
        attempted_sensitive = True

    # Anonymous telemetry only
    log_event({
        "event_type": "submit",
        "attempted_sensitive": attempted_sensitive,
        "fields_filled": sum(bool(x) for x in [name, number, exp, cvv]),
        "variant": "A"
    })

    if attempted_sensitive:
        return render_template(
            "index.html",
            message="⚠️ Training: never enter real payment data on pages like this. Your submission was blocked and not stored.",
            message_type="warn",
        ), 200
    else:
        return render_template(
            "index.html",
            message="✅ Training complete. You used test-like placeholders. No data was stored.",
            message_type="ok",
        ), 200

@app.get("/report")
def report():
    counts = {"total": 0, "submits": 0, "blocked": 0, "safe": 0}
    try:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                counts["total"] += 1
                try:
                    e = json.loads(line)
                except Exception:
                    continue
                if e.get("event_type") == "submit":
                    counts["submits"] += 1
                    if e.get("attempted_sensitive"):
                        counts["blocked"] += 1
                    else:
                        counts["safe"] += 1
    except FileNotFoundError:
        pass
    return render_template("report.html", counts=counts)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
