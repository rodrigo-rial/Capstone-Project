from bot.bot_instance import bot, dataset
from bot import utils, responses
from bot import transformer 
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    botones = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton("Analizar Imagen", callback_data="imagen")
    btn2 = InlineKeyboardButton("Analizar sentimiento", callback_data="sentimiento")
    btn3 = InlineKeyboardButton("")
    botones.add(btn1, btn2)
    bot.reply_to(message, "¡Hola!, Soy MediBot, tu asistente de primeros auxilios. ¿Cuál es tu emergencia?", reply_markup = botones)

@bot.message_handler(func=lambda message: True)
def responder(message):
    if message.text is None:
        bot.reply_to(message, "Por favor, envíame tu consulta como un mensaje de texto.")
        return

    pregunta = message.text

    #obtiene analisis de emergencia
    analisis = transformer.analizar(pregunta)
    nivel_urgencia = analisis['nivel_urgencia']
    respuesta_base_ia = analisis['respuesta_ia']

    # decide accion en base a urgencia
    
    if nivel_urgencia == "ALTA":
        respuesta_dataset = responses.buscar_en_dataset(pregunta, dataset)
        
        if respuesta_dataset:
            # CASO 1: URGENCIA ALTA + ENCONTRADO EN DATASET
            respuesta_final = (
                f"**[EMERGENCIA]**\n"
                f"{respuesta_dataset}\n\n"
                f"-------------------------------------\n"
                f"**ADVERTENCIA:** {respuesta_base_ia}"
            )
            bot.reply_to(message, respuesta_final, parse_mode="Markdown")
        else:
            # CASO 2: URGENCIA ALTA + GROQ (NO HAY RTA EN DATASET)
            bot.send_chat_action(message.chat.id, 'typing') # informa que está "pensando"
            respuesta_ia_groq = responses.respuesta_groq(pregunta)
            
            respuesta_final = (
                f"**[test IA - EMERGENCIA]**\n"
                f"{respuesta_ia_groq}\n\n"
                f"-------------------------------------\n"
                f"**ADVERTENCIA IMPORTANTE:** {respuesta_base_ia}"
            )
            bot.reply_to(message, respuesta_final, parse_mode="Markdown")

    elif nivel_urgencia == "MEDIA" or nivel_urgencia == "MEDIA_NO_MEDICA":
        # incluye quejas médicas leves O quejas emocionales
        respuesta_dataset = responses.buscar_en_dataset(pregunta, dataset)
        
        if respuesta_dataset:
            # CASO 3: URGENCIA MEDIA + ENCONTRADO EN DATASET
            respuesta_final = (
                f"**[RECOMENDACIÓN]**\n"
                f"{respuesta_dataset}\n\n"
                f"**rta. base sentimientos:** {respuesta_base_ia}"
            )
            bot.reply_to(message, respuesta_final, parse_mode="Markdown")
        else:
            # CASO 4: MEDIA_NO_MEDICA O MEDIA sin match en dataset. Llamamos a Groq.
            bot.send_chat_action(message.chat.id, 'typing')
            respuesta_ia_groq = responses.respuesta_groq(pregunta)
            
            respuesta_final = (
                f"**[RECOMENDACIÓN DE IA]**\n"
                f"{respuesta_ia_groq}\n\n"
                f"**rta. base sentimientos:** {respuesta_base_ia}"
            )
            bot.reply_to(message, respuesta_final, parse_mode="Markdown")

    elif nivel_urgencia == "BAJA":
        if respuesta_base_ia == "INFO_NO_MEDICA_O_SALUDO":
            # CASO 5: pregunta social/informativa, llama a Groq.
            bot.send_chat_action(message.chat.id, 'typing')
            respuesta_ia_groq = responses.respuesta_groq(pregunta)
            bot.reply_to(message, respuesta_ia_groq)
        else:
            # CASO 6: Urgencia BAJA (me siento bien p. ej), no necesitamos Groq.
            bot.reply_to(message, respuesta_base_ia)

    else: 
        # CASO 7: ERROR, usamos a groq por las dudas
        bot.send_chat_action(message.chat.id, 'typing')
        respuesta_ia_groq = responses.respuesta_groq(pregunta)
        bot.reply_to(message, respuesta_ia_groq)