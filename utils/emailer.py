import smtplib
import time
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
load_dotenv()

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
def send_email(content, receivers):

    if isinstance(receivers, str):
        receivers = [r.strip() for r in receivers.split(",")]

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL_SENDER, EMAIL_PASSWORD)

    for r in receivers:
        msg = MIMEText(content, "html")
        msg["Subject"] = "🧠 AI Tech News"
        # msg["From"] = EMAIL_SENDER
        msg["From"] = f"AI News Digest <{EMAIL_SENDER}>"  #if don't want to show email address, just put name here
        msg["To"] = r

        server.sendmail(EMAIL_SENDER, r, msg.as_string())
        time.sleep(2)

    server.quit()