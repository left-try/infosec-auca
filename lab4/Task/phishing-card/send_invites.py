import os, smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_HOST = os.environ.get("SMTP_HOST")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASS = os.environ.get("SMTP_PASS")
FROM_EMAIL = os.environ.get("FROM_EMAIL", SMTP_USER)
TO_EMAIL   = os.environ.get("TO_EMAIL")  # single test recipient
TRAINING_URL = os.environ.get("TRAINING_URL", "http://127.0.0.1:8000")

def main():
    missing = [k for k,v in {
        "SMTP_HOST":SMTP_HOST, "SMTP_USER":SMTP_USER, "SMTP_PASS":SMTP_PASS,
        "FROM_EMAIL":FROM_EMAIL, "TO_EMAIL":TO_EMAIL
    }.items() if not v]
    if missing:
        print("Missing env vars:", ", ".join(missing))
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Security Awareness Training — Simulated Checkout Exercise"
    msg["From"] = FROM_EMAIL
    msg["To"] = TO_EMAIL

    text = f"""This is an authorized training exercise for your Information Security course.
Visit: {TRAINING_URL}
Do NOT enter real personal or payment information.
Use only the placeholders shown on the page.
After the exercise, view anonymized metrics at {TRAINING_URL}/report.
"""
    html = f"""<html><body style="font-family:Arial,sans-serif">
<p>This is an <strong>authorized training exercise</strong> for your Information Security course.</p>
<p>Visit: <a href="{TRAINING_URL}">{TRAINING_URL}</a></p>
<ul>
  <li><strong>Do not</strong> enter real personal or payment information.</li>
  <li>Use only the placeholders shown on the page.</li>
</ul>
<p>After the exercise, view anonymized metrics at
<a href="{TRAINING_URL}/report">{TRAINING_URL}/report</a>.</p>
</body></html>"""

    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))

    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls(context=context)
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(FROM_EMAIL, [TO_EMAIL], msg.as_string())
    print("Invite sent.")

if __name__ == "__main__":
    main()
