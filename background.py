from flask import Flask
from flask import request
from threading import Thread
import time
import requests
from datetime import datetime


app = Flask('')

@app.route('/')
def home():
    return "I'm alive"

def run():
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print("Time on start =", dt_string)
    app.run(host="0.0.0.0", port=80)
    

def keep_alive():
    t = Thread(target=run)
    t.start()