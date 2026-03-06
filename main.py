import os
from flask import Flask, request
import telebot
from supabase import create_client

TOKEN = os.getenv("TOKEN")
URL = os.getenv("URL_APP")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=URL + TOKEN)
    return "Bot funcionando", 200


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Hola! usa /buscar producto")


@bot.message_handler(commands=['buscar'])
def buscar_producto(message):

    query = message.text.replace('/buscar', '').strip()

    if query == "":
        bot.reply_to(message, "Ejemplo: /buscar laptop")
        return

    response = supabase.table("productos").select("*").ilike("nombre", f"%{query}%").execute()

    data = response.data

    if len(data) > 0:

        respuesta = "Resultados:\n\n"

        for item in data:
            respuesta += f"{item['nombre']}\nPrecio: ${item['precio']}\nStock: {item['stock']}\n\n"

        bot.reply_to(message, respuesta)

    else:
        bot.reply_to(message, "Producto no encontrado")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)