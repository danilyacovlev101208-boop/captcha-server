from flask import Flask, request
from flask_cors import CORS
import requests


app = Flask(__name__)

CORS(app)


@app.route("/")
def home():
    return "Server works!"


@app.route("/verify", methods=["POST"])
def verify():

    ip = request.headers.get(
        "X-Forwarded-For",
        request.remote_addr
    )


    info = requests.get(
        f"https://ipwho.is/{ip}"
    ).json()


    return {
        "ip": ip,
        "country": info.get("country"),
        "city": info.get("city"),
        "provider": info.get("connection", {}).get("isp")
    }


app.run(
    host="0.0.0.0",
    port=5000
)
