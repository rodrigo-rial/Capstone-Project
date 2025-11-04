from bot.bot_instance import bot, dataset
from bot import utils, responses

@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(message, "¡Hola!, Soy Auxi.IA, tu asistente de primeros auxilios. ¿Cuál es tu emergencia?")

@bot.message_handler(func=lambda message: True)
def responder(message):
    pregunta = message.text

    if utils.es_emergencia(pregunta):
        respuesta_dataset = responses.buscar_en_dataset(pregunta, dataset)
        if respuesta_dataset:
            bot.reply_to(message, respuesta_dataset)
        else:
            bot.reply_to(message, "Parece una emergencia. LLamá al 107 o buscá ayuda médica inmediata.")
    else:
        respuesta_ia = responses.respuesta_groq(pregunta)
        bot.reply_to(message, respuesta_ia)