import os
import threading
import time
import requests
import logging
from flask import Flask
from threading import Thread

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask("")

@app.route("/")
def home():
    return "Bot is alive!"

@app.route("/health")
def health_check():
    return "OK", 200

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def ping_self():
    time.sleep(120) 
    while True:
        url = os.environ.get("RENDER_EXTERNAL_URL") or os.environ.get("CUSTOM_URL")
        if url:
            try:
                if not url.startswith("http"):
                    url = "https://" + url
                health_url = f"{url.rstrip('/')}/health"
                response = requests.get(health_url, timeout=120)
                logger.info(f"Self-ping status: {response.status_code}")
            except Exception as e:
                logger.warning(f"Self-ping skipped (app might be starting): {e}")
        
        time.sleep(14 * 60)

def keep_alive():
    t1 = Thread(target=run, daemon=True)
    t1.start()
    
    t2 = Thread(target=ping_self, daemon=True)
    t2.start()
