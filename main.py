from flask import Flask, request
from flask_cors import CORS
import requests
import telebot


app = Flask(__name__)
CORS(app)


# Вставь сюда НОВЫЙ токен после перевыпуска в BotFather
BOT_TOKEN = "8695680481:AAHhVE5b3eft3t27Mt61QDxWaltnl0CCgEc"

bot = telebot.TeleBot(BOT_TOKEN)


@app.route("/")
def home():
    return "Server works!"


@app.route("/verify", methods=["POST"])
def verify():

    data = request.json

    telegram_id = data.get("id")
    username = data.get("username", "unknown")


    # Получаем IP пользователя
    ip = request.headers.get(
        "X-Forwarded-For",
        request.remote_addr
    )

    # Если прокси передал несколько IP
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



    country = geo.get("country", "неизвестно")
    city = geo.get("city", "неизвестно")
    region = geo.get("region", "неизвестно")

    timezone = geo.get(
        "timezone",
        {}
    ).get(
        "id",
        "неизвестно"
    )

    latitude = geo.get(
        "latitude",
        "нет"
    )

    longitude = geo.get(
        "longitude",
        "нет"
    )


    connection = geo.get(
        "connection",
        {}
    )

    isp = connection.get(
        "isp",
        "неизвестно"
    )

    asn = connection.get(
        "asn",
        "неизвестно"
    )


    message = f"""
🌐 Новая проверка

👤 Пользователь:
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


🔢 AS:
{asn}
"""


    # Отправляем пользователю сообщение
    if telegram_id:

        try:

            bot.send_message(
                telegram_id,
                message
            )

        except Exception as e:

            print(
                "Ошибка Telegram:",
                e
            )


    return {
        "success": True,

        "ip": ip,
        "country": country,
        "city": city,
        "provider": isp
    }



if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )
