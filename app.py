from flask import Flask, send_file, send_from_directory, request, Response
from dotenv import load_dotenv
load_dotenv()
import os
import json
from mongoengine import *
from flask_cors import CORS
from python_script import login as login
from python_script import twilio_functions as twilio_fn
from python_script import items_functions as items_func
import requests
from pymongo.mongo_client import MongoClient
import pymongo
import os
from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from twilio.request_validator import RequestValidator
from apscheduler.schedulers.background import BackgroundScheduler
import atexit


app = Flask(__name__, static_folder="build")
cors = CORS(app)
app.config["CORS-HEADERS"] = "Content-Type"

host = os.getenv("mongodb+srv://superuser:oNhrJylyRbxW2wKa@emrgcall.pgoqiio.mongodb.net/?retryWrites=true&w=majority&appName=emrgcall")
connect(db='emrgcallnew', host=host)


def call_again():
    try:
        print("call_again")
        twilio_fn.call_again()
    except:
        pass

# Create a scheduler
scheduler = BackgroundScheduler()
# Add the job to run every 10 minutes
scheduler.add_job(func=call_again, trigger="interval", minutes=0.5)
# Start the scheduler
scheduler.start()
# Ensure scheduler stops when the app exits
atexit.register(lambda: scheduler.shutdown())


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def index(path):
    if (path != "" and os.path.exists(app.static_folder + "/" + path)):
        return send_from_directory(app.static_folder + "/", path)
    else:
        return send_from_directory(app.static_folder, "index.html")


@app.route("/api/login", methods=["POST"])
def login_request():
    data = dict(json.loads(request.data.decode('utf-8')))
    print(data)
    return login.login_request(data)

# users functions


@app.route("/api/add_worker", methods=["POST"])
def add_worker():
    data = dict(json.loads(request.data.decode('utf-8')))
    return items_func.add_worker(data)


@app.route("/api/get_worker", methods=["POST"])
def get_worker():
    data = dict(json.loads(request.data.decode('utf-8')))
    return items_func.get_worker(data)


@app.route("/api/edit_worker", methods=["POST"])
def edit_worker():
    data = dict(json.loads(request.data.decode('utf-8')))
    return items_func.edit_worker(data)


@app.route("/api/delete_worker", methods=["POST"])
def delete_worker():
    data = dict(json.loads(request.data.decode('utf-8')))
    return items_func.delete_worker(data)


@app.route("/api/delete_report", methods=["POST"])
def delete_report():
    data = dict(json.loads(request.data.decode('utf-8')))
    return items_func.delete_report(data)


@app.route("/api/get_jobs_departments", methods=["POST"])
def get_jobs_departments():
    data = dict(json.loads(request.data.decode('utf-8')))
    return items_func.get_jobs_departments(data)

# user tutorial


@app.route("/api/send_alert", methods=["POST"])
def send_alert():
    data = dict(json.loads(request.data.decode('utf-8')))
    return twilio_fn.send_alert(data)

# user tutorial


@app.route("/api/handle_key", methods=["POST"])
def handle_key():
    print(request.form.to_dict())
    return twilio_fn.handle_key(request.form.to_dict())

# user tutorial


@app.route("/api/get_balance", methods=["POST"])
def get_balance():
    data = dict(json.loads(request.data.decode('utf-8')))
    return twilio_fn.get_balance(data)

# user tutorial


@app.route("/api/get_reports", methods=["POST"])
def get_reports():
    data = dict(json.loads(request.data.decode('utf-8')))
    return items_func.get_reports(data)

# user tutorial


@app.route("/api/get_report", methods=["POST"])
def get_report():
    data = dict(json.loads(request.data.decode('utf-8')))
    return items_func.get_report(data)


# app.run(port=5050, debug=True)
# app.run(debug=False)

# port = int(os.environ.get('PORT', 5050))  # Get the port from the environment or use 5000
# app.run( port=port)
app.run(host='0.0.0.0')  # Run the app on the server's default port
