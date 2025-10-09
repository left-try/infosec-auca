from flask import Flask, request, abort, jsonify
import os
from datetime import datetime

app = Flask(__name__)
UPLOAD_DIR = "received_logs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
EXPECTED_TOKEN = "LAB_SECRET_TOKEN_ABC123"

def check_auth():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return False
    token = auth.split(" ", 1)[1]
    return token == EXPECTED_TOKEN

@app.route("/upload", methods=["POST"])
def upload():
    if not check_auth():
        return abort(401, "Unauthorized")
    if "file" not in request.files:
        return abort(400, "No file part")
    f = request.files["file"]
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"upload_{ts}.txt"
    path = os.path.join(UPLOAD_DIR, filename)
    f.save(path)
    return jsonify({"status": "ok", "saved_as": filename})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
