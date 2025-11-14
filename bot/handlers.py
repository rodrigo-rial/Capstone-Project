import datetime
import requests
import json
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.bot_instance import bot, dataset, MEMORIA_CONVERSACION
from bot import utils, responses
from bot import transformer 
from bot.voz import transcribir_voz_con_groq 
from bot.vision import imagen_a_base64, describir_imagen_con_groq
from bot.responses import respuesta_groq_contextual
from config import URL_API_DEA

TIEMPO_LIMITE_CONTEXTO = 300 

USUARIOS_EN_MODO_SENTIMIENTO = set()

def _obtener_contexto(chat_id):
    if chat_id in MEMORIA_CONVERSACION:
        contexto = MEMORIA_CONVERSACION[chat_id]
        tiempo_guardado = contexto['marca_tiempo']
        
        if (datetime.datetime.now() - tiempo_guardado).total_seconds() > TIEMPO_LIMITE_CONTEXTO:
            del MEMORIA_CONVERSACION[chat_id] 
            return None
        
        return contexto['respuesta_bot']
    return None

@bot.message_handler(commands=["start"])
def enviar_bienvenida(message):
    if message.chat.id in MEMORIA_CONVERSACION:
        del MEMORIA_CONVERSACION[message.chat.id]

    botones = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton("Analizar texto", callback_data="texto")
    btn2 = InlineKeyboardButton("Analizar voz", callback_data="voz")
    btn3 = InlineKeyboardButton("Analizar imagen", callback_data="imagen")
    btn4 = InlineKeyboardButton("Analizar Sentimiento", callback_data="sentimiento")
    btn5 = InlineKeyboardButton("🛈 Acerca de mi", callback_data="acerca")
    btn6 = InlineKeyboardButton("Ayuda", callback_data="ayuda")
    botones.add(btn1, btn2, btn3, btn4, btn5, btn6)
    bot.reply_to(message, "🤖 ¡Hola!, Soy MediBot, tu asistente de primeros auxilios. ¿Cuál es tu emergencia?", reply_markup = botones)

@bot.callback_query_handler(func=lambda call:True)
def callback(call):
    bot.answer_callback_query(call.id)
    chat_id = call.message.chat.id

    if call.data == "texto":    
        bot.send_message(
            chat_id,
            "*TEXTO* \n\n"
            "🩺 Contame por *texto* tu emergencia y te brindo la información necesaria para actuar correctamente hasta que llegue ayuda profesional! "
        )
        
    elif call.data == "voz":
        bot.send_message(
            chat_id,
            "*AUDIO* \n\n"
            "🎙️ Por favor, enviá un *audio* contando tu emergencia. Con esa información voy a guiarte paso a paso con las indicaciones de primeros auxilios más adecuadas."
        )
            
    elif call.data == "imagen":
        bot.send_message(
            chat_id,
            "*IMAGEN* \n\n"
            "📸 Enviá una *imagen clara* de la herida o la zona afectada. Con esa información puedo analizarla y orientarte sobre el tipo de lesión y los primeros auxilios recomendados."
        )
            
    elif call.data == "sentimiento":
        manejar_comando_sentimientos(call.message, desde_callback=True) 
            
    elif call.data == "acerca":
        bot.send_message(
            chat_id,
            "*ACERCA DE MI* \n\n"
            "🤖 Soy *MediBot*, tu asistente de primeros auxilios desarrollado por el equipo *Coffe&Code* del *Samsung Innovation Campus*. Estoy diseñado para orientarte ante emergencias leves, brindando información rápida y confiable. 🚑"
        )

    elif call.data == "ayuda":
        enviar_ayuda(call.message)

@bot.message_handler(commands=["dea", "desfibrilador"])
def pedir_ubicacion_dea(message):
    markup_reply = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    boton_ubicacion = types.KeyboardButton("Compartir mi Ubicación 📍", request_location=True)
    markup_reply.add(boton_ubicacion)
    
    markup_inline = types.InlineKeyboardMarkup()
    btn_registrar = types.InlineKeyboardButton("Registrar un nuevo DEA ➕", url="https://docs.google.com/forms/d/e/1FAIpQLSfovRZj341Dgq3rcoqyyal79DRmgN6BedNLIyjsyJePhQh4fg/viewform")
    markup_inline.add(btn_registrar)
    
    bot.reply_to(message, 
        "Entendido. Para encontrar el DEA verificado más cercano, necesito tu ubicación actual (usa el botón de abajo).\n\n"
        "Si conoces un DEA que no está en el mapa, ¡ayúdanos a registrarlo! Utilizamos los datos\n"
        "de la fundación UDEC para apoyarnos en este proyecto.",
        reply_markup=markup_inline
    )
    
    bot.send_message(message.chat.id, "Presiona aquí para compartir tu ubicación:", reply_markup=markup_reply)


@bot.message_handler(commands=["texto", "audio", "imagen", "ayuda", "help"])
def enviar_ayuda(message):
    comando = message.text.lower()
    
    texto_ayuda = (
        "ℹ️ Puedo ayudarte de distintas formas:\n\n"
        "- 📄 Recibir emergencias por texto.\n"
        "- 🎙️ Analizar audios para guiarte paso a paso.\n"
        "- 📸 Identificar heridas mediante imágenes.\n"
        "- 💬 Analizar el tono emocional de tu mensaje.\n"
        "- 📍 Encontrar el /dea (Desfibrilador) más cercano.\n\n"
        "Podés reiniciar la conversación en cualquier momento enviando */start*.\n\n"
        "*Comandos*\n"
        "- */texto*\n"
        "- */imagen*\n"
        "- */sentimientos*\n"
        "- */dea*\n"
        "- */ayuda* o */help*"
    )
    
    markup = types.InlineKeyboardMarkup()
    btn_registrar_dea = types.InlineKeyboardButton("Registrar un nuevo DEA ➕", url="https://docs.google.com/forms/d/e/1FAIpQLSfovRZj341Dgq3rcoqyyal79DRmgN6BedNLIyjsyJePhQh4fg/viewform")
    markup.add(btn_registrar_dea)

    if comando == "/texto":
        bot.reply_to(
            message,
            "*TEXTO* \n\n"
            "🩺 Contame por *texto* tu emergencia y te brindo la información necesaria para actuar correctamente hasta que llegue ayuda profesional! "
        )    
    
    elif comando == "/audio":
        bot.reply_to(
            message,
            "*AUDIO* \n\n"
            "🎙️ Por favor, enviá un *audio* contando tu emergencia. Con esa información voy a guiarte paso a paso con las indicaciones de primeros auxilios más adecuadas."
        )
            
    elif comando == "/imagen":
        bot.reply_to(
            message,
            "*IMAGEN* \n\n"
            "📸 Enviá una *imagen clara* de la herida o la zona afectada. Con esa información puedo analizarla y orientarte sobre el tipo de lesión y los primeros auxilios recomendados."
        )
            
    elif comando in ["/ayuda", "/help"]:
        bot.reply_to(
            message,
            texto_ayuda,
            reply_markup=markup
        )

@bot.message_handler(content_types=['location'])
def manejar_ubicacion_dea(message):
    lat_usuario = message.location.latitude
    lon_usuario = message.location.longitude
    chat_id = message.chat.id

    markup_remove = types.ReplyKeyboardRemove()
    bot.send_message(chat_id, "Buscando DEA verificado más cercano en la base de datos de AWS...", reply_markup=markup_remove)
    bot.send_chat_action(chat_id, 'typing')

    parametros = {'lat': lat_usuario, 'lon': lon_usuario}

    try:
        respuesta_api = requests.get(URL_API_DEA, params=parametros, timeout=10)

        if respuesta_api.status_code == 200:
            datos = respuesta_api.json()

            if isinstance(datos.get("body"), str):
                datos = json.loads(datos["body"])

            if "dea_cercano" not in datos:
                bot.reply_to(message,
                    "⚠️ No se encontró información del DEA más cercano. Llama al 107 (Emergencias Médicas).")
                return

            dea = datos["dea_cercano"]

            distancia = dea.get("distancia_km", "N/A")
            nombre = dea.get("nombre_lugar", "DEA Cercano")
            direccion = dea.get("direccion", "Dirección no disponible")
            lat_dea = dea.get("latitud")
            lon_dea = dea.get("longitud")

            mapa_link = f"https://www.google.com/maps/search/?api=1&query={lat_dea},{lon_dea}"

            mensaje_respuesta = (
                f"🚨 **DEA VERIFICADO ENCONTRADO** 🚨\n\n"
                f"**Lugar:** {nombre}\n"
                f"**Distancia:** {distancia} km\n"
                f"**Dirección:** {direccion}\n\n"
                f"[ABRIR EN GOOGLE MAPS]({mapa_link})"
            )

            bot.reply_to(message, mensaje_respuesta, parse_mode="Markdown")
            bot.send_location(chat_id, lat_dea, lon_dea)

        elif respuesta_api.status_code == 404:
            bot.reply_to(message,
                "⚠️ No se encontró ningún DEA verificado cerca de tu ubicación. Llama al 107 (Emergencias Médicas).")
        else:
            bot.reply_to(message,
                f"🚫 Hubo un error al consultar la base de datos de DEAs (Error: {respuesta_api.status_code}). Llama al 107.")

    except requests.exceptions.RequestException as e:
        print(f"Error de conexión a la API de AWS: {e}")
        bot.reply_to(message,
            "❌ No se pudo conectar con el servicio de localización de DEAs. Verifica tu conexión o llama al 107.")

@bot.message_handler(commands=["sentimientos"])
def manejar_comando_sentimientos(message, desde_callback=False):
    chat_id = message.chat.id
    USUARIOS_EN_MODO_SENTIMIENTO.add(chat_id)
    
    texto_respuesta = (
        "*SENTIMIENTOS* \n\n"
        "🧠 Entendido. Enviá tu próximo *mensaje de voz o texto*.\n\n"
        "_(Lo analizaré por su tono emocional **y también** por cualquier emergencia)._"
    )
    
    if desde_callback:
        bot.send_message(chat_id, texto_respuesta, parse_mode="Markdown")
    else:
        bot.reply_to(message, texto_respuesta, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def responder(message):
    if message.text is None:
        bot.reply_to(message, "Por favor, envíame tu consulta como un mensaje de texto.")
        return

    chat_id = message.chat.id
    pregunta = message.text.lower() 

    respuesta_de_sentimiento = "" 

    if chat_id in USUARIOS_EN_MODO_SENTIMIENTO:
        analisis = transformer.analizar_sentimiento_texto(pregunta)
        
        if "error" not in analisis:
            sentimiento = analisis['sentimiento']
            confianza = analisis['confianza'] * 100
            
            respuesta_de_sentimiento = f"🤖 **Análisis de Sentimiento:**\n"
            if sentimiento == "NEG":
                respuesta_de_sentimiento += f"Detecto un sentimiento **Negativo** ({confianza:.1f}%).\n"
            elif sentimiento == "NEU":
                respuesta_de_sentimiento += f"Detecto un tono **Neutral** ({confianza:.1f}%).\n"
            elif sentimiento == "POS":
                respuesta_de_sentimiento += f"Detecto un sentimiento **Positivo** ({confianza:.1f}%).\n"
            
            respuesta_de_sentimiento += "-------------------------------------\n\n"
        
        USUARIOS_EN_MODO_SENTIMIENTO.remove(chat_id)

    contexto_previo = _obtener_contexto(chat_id)
    
    if contexto_previo:
        bot.send_chat_action(chat_id, 'typing')
        respuesta_ia_groq = responses.respuesta_groq_contextual(
            mensaje_usuario=pregunta,
            contexto_previo=contexto_previo
        )
        respuesta_final = (
            f"{respuesta_de_sentimiento}"
            f"_{respuesta_ia_groq}_"
        )
        bot.reply_to(message, respuesta_final, parse_mode="Markdown")
        MEMORIA_CONVERSACION[chat_id] = {
            "respuesta_bot": respuesta_ia_groq, 
            "marca_tiempo": datetime.datetime.now()
        }
        return 

    bot.send_chat_action(chat_id, 'typing')

    analisis_urgencia = transformer.clasificar_urgencia_por_palabras(pregunta)
    nivel_urgencia = analisis_urgencia["nivel_urgencia"]
    advertencia = analisis_urgencia["advertencia_ia"]
    
    respuesta_dataset = responses.buscar_en_dataset(pregunta, dataset)

    if respuesta_dataset:
        respuesta_final = ""
        if nivel_urgencia == "ALTA":
            respuesta_final = (
                f"🚨 **[EMERGENCIA]** 🚨\n"
                f"{respuesta_dataset}\n\n"
                f"-------------------------------------\n"
                f"⚠️ **ADVERTENCIA IMPORTANTE:** {advertencia}"
            )
        
        elif nivel_urgencia == "MEDIA":
            respuesta_final = (
                f"🩺 **[RECOMENDACIÓN DE CUIDADO]** 🩹\n"
                f"{respuesta_dataset}\n\n"
                f"-------------------------------------\n"
                f"*{advertencia}*"
            )
        
        else: 
            respuesta_final = (
                f"✅ **[CONSULTA INFORMATIVA]** 👍\n"
                f"{respuesta_dataset}"
            )

        bot.reply_to(message, respuesta_de_sentimiento + respuesta_final, parse_mode="Markdown")
        
        MEMORIA_CONVERSACION[chat_id] = {
            "respuesta_bot": respuesta_dataset,
            "marca_tiempo": datetime.datetime.now()
        }
        
    else:
        respuesta_ia_groq = responses.respuesta_groq(pregunta)
        respuesta_final = ""
        
        if nivel_urgencia == "ALTA":
            respuesta_final = (
                f"🚨 **[RESPUESTA IA - EMERGENCIA]** 🚨\n"
                f"{respuesta_ia_groq}\n\n"
                f"-------------------------------------\n"
                f"⚠️ **ADVERTENCIA IMPORTANTE:** {advertencia}"
            )
        
        elif nivel_urgencia == "MEDIA":
            respuesta_final = (
                f"🩺 **[ORIENTACIÓN POR IA]** 🩹\n"
                f"{respuesta_ia_groq}\n\n"
                f"-------------------------------------\n"
                f"*{advertencia}*"
            )

        else: 
            respuesta_final = respuesta_ia_groq 

        bot.reply_to(message, respuesta_de_sentimiento + respuesta_final, parse_mode="Markdown")
        
        MEMORIA_CONVERSACION[chat_id] = {
            "respuesta_bot": respuesta_ia_groq,
            "marca_tiempo": datetime.datetime.now()
        }

@bot.message_handler(content_types=['photo'])
def manejar_foto(mensaje):
    try:
        chat_id = mensaje.chat.id
        bot.reply_to(mensaje, "📷 He recibido tu imagen. Permite un momento mientras la analizo...")
        
        foto = mensaje.photo[-1]
        info_archivo = bot.get_file(foto.file_id)
        archivo_descargado = bot.download_file(info_archivo.file_path)
        
        imagen_base64 = imagen_a_base64(archivo_descargado)

        if not imagen_base64:
            bot.reply_to(mensaje, "Lo siento, ocurrió un error al procesar el formato de la imagen. Intenta de nuevo.")
            return
        
        descripcion = describir_imagen_con_groq(imagen_base64)
        
        if descripcion:
            respuesta_final = (
                f"👁️ **ANÁLISIS DE IMAGEN (IA)** 👁️\n\n"
                f"**Observaciones y Recomendaciones:**\n"
                f"_{descripcion}_"
            )
            bot.reply_to(mensaje, respuesta_final, parse_mode='Markdown')
            
            MEMORIA_CONVERSACION[chat_id] = {
                "respuesta_bot": descripcion, 
                "marca_tiempo": datetime.datetime.now()
            }
        else:
            bot.reply_to(mensaje, "No pude analizar el contenido de la imagen. Por favor intenta con otra.")
    
    except Exception as e:
        print(f"Error grave al procesar la imagen: {e}")
        bot.reply_to(mensaje, "Ocurrió un error inesperado al procesar tu imagen. El equipo técnico ha sido notificado.")

@bot.message_handler(content_types=['voice'])
def manejar_voz(message):
    try:
        if message.chat.id in USUARIOS_EN_MODO_SENTIMIENTO:
             bot.reply_to(message, "🎙️ Entendido. Analizando tu audio, por favor espera...")
        else:
             bot.reply_to(message, "🎙️ Entendido. Transcribiendo tu audio, por favor espera...")

        texto_transcrito = transcribir_voz_con_groq(message)
        
        if not texto_transcrito:
            bot.reply_to(message, "Lo siento, no pude entender lo que dijiste en el audio. ¿Puedes intentarlo de nuevo o escribirlo?")
            if message.chat.id in USUARIOS_EN_MODO_SENTIMIENTO:
                USUARIOS_EN_MODO_SENTIMIENTO.remove(message.chat.id)
            return

        if message.chat.id not in USUARIOS_EN_MODO_SENTIMIENTO:
            bot.reply_to(message, f"_[Has dicho]: {texto_transcrito}_ \n\nProcesando tu consulta...", parse_mode="Markdown")

        message.text = texto_transcrito
        
        responder(message) 
    
    except Exception as e:
        print(f"Error grave al procesar el audio: {e}")
        bot.reply_to(message, "Ocurrió un error inesperado al procesar tu audio.")
        if message.chat.id in USUARIOS_EN_MODO_SENTIMIENTO:
            USUARIOS_EN_MODO_SENTIMIENTO.remove(message.chat.id)