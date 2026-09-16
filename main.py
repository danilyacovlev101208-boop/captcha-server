from flask import Flask, request
from flask_cors import CORS
import requests
import os


app = Flask(__name__)

CORS(app)


# Cloudflare Turnstile Secret Key
TURNSTILE_SECRET = os.getenv(
    "TURNSTILE_SECRET"
)


@app.route("/")
def home():

    return "Server works!"


@app.route("/verify", methods=["POST"])
def verify():

    data = request.json


    # Получаем данные из Mini App
    telegram_id = data.get(
        "id"
    )

    username = data.get(
        "username",
        "unknown"
    )


    # Получаем Cloudflare token
    turnstile_token = data.get(
        "turnstile_token"
    )


    if not turnstile_token:

        return {
            "success": False,
            "error": "No Cloudflare token"
        }, 400



    # Проверка Cloudflare
    try:

        cloudflare_check = requests.post(

            "https://challenges.cloudflare.com/turnstile/v0/siteverify",

            data={

                "secret": TURNSTILE_SECRET,

                "response": turnstile_token

            },

            timeout=10

        )


        cloudflare_result = cloudflare_check.json()



    except Exception as e:


        return {

            "success": False,

            "error": str(e)

        }, 500



    # Если Cloudflare не подтвердил

    if not cloudflare_result.get(
        "success"
    ):

        return {

            "success": False,

            "error": "Cloudflare verification failed"

        }, 403



    # Получаем IP пользователя

    ip = request.headers.get(
        "X-Forwarded-For",
        request.remote_addr
    )


    # Если несколько IP через прокси

    if ip and "," in ip:

        ip = ip.split(",")[0].strip()



    # Получаем информацию об IP

    try:

        geo = requests.get(

            f"https://ipwho.is/{ip}",

            timeout=10

        ).json()


    except Exception:


        geo = {}



    result = {


        "success": True,


        "telegram_id": telegram_id,


        "username": username,


        "ip": ip,


        "country":
        geo.get("country"),


        "city":
        geo.get("city"),


        "region":
        geo.get("region"),


        "timezone":
        geo.get("timezone", {}).get("id"),


        "latitude":
        geo.get("latitude"),


        "longitude":
        geo.get("longitude"),


        "provider":
        geo.get("connection", {}).get("isp"),


        "asn":
        geo.get("connection", {}).get("asn")

    }



    return result



if __name__ == "__main__":


    app.run(

        host="0.0.0.0",

        port=5000

    )
