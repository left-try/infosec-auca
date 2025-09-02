#!/usr/bin/env python3
import os
import time
import shlex
import hashlib
from datetime import datetime

def list_items_older_than(date_input):
    try:
        target_date = datetime.strptime(date_input, "%Y-%m-%d").timestamp()
        items = os.listdir('.')
        for item in sorted(items):
            try:
                item_ctime = os.path.getctime(item)
            except OSError:
                continue
            if item_ctime < target_date:
                item_type = "Folder" if os.path.isdir(item) else "File"
                creation_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item_ctime))
                print(f"{item} ({item_type}, Created: {creation_time})")
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")

def sha256_file(path):
    if not os.path.isfile(path):
        print(f"Not a regular file: {path}")
        return
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        print(f"SHA-256({path}) = {h.hexdigest()}")
    except OSError as e:
        print(f"Error reading {path}: {e}")

HELP = """Toy Shell commands:
  YYYY-MM-DD        List files/folders in current dir created before this date.
  hash <file>       Compute SHA-256 of <file>.
  help              Show this message.
  exit              Quit.
"""

def toy_shell():
    print("Toy Shell: date-based listing and SHA-256 hashing")
    print("Type 'help' for commands. Enter a date (YYYY-MM-DD) or 'hash <file>' or 'exit'.")
    while True:
        try:
            line = input("toy-shell> ").strip()
            if not line:
                continue
            if line.lower() == "exit":
                print("Exiting toy shell.")
                break
            if line.lower() == "help":
                print(HELP)
                continue

            parts = shlex.split(line)
            cmd = parts[0].lower()

            if cmd == "hash":
                if len(parts) != 2:
                    print("Usage: hash <file>")
                    continue
                sha256_file(parts[1])
                continue

            list_items_older_than(line)

        except KeyboardInterrupt:
            print("\nUse 'exit' to quit the shell.")

if __name__ == "__main__":
    toy_shell()

