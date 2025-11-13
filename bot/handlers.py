import datetime
import requests
from telebot import types
from bot.bot_instance import bot, dataset, MEMORIA_CONVERSACION
from bot import utils, responses
from bot import transformer 
from bot.voz import transcribir_voz_con_groq 
from bot.vision import imagen_a_base64, describir_imagen_con_groq
from bot.responses import respuesta_groq_contextual
from config import URL_API_DEA

TIEMPO_LIMITE_CONTEXTO = 300 #5min

def _obtener_contexto(chat_id):
    if chat_id in MEMORIA_CONVERSACION:
        contexto = MEMORIA_CONVERSACION[chat_id]
        tiempo_guardado = contexto['marca_tiempo']
        
        # comprueba si el contexto expiró
        if (datetime.datetime.now() - tiempo_guardado).total_seconds() > TIEMPO_LIMITE_CONTEXTO:
            del MEMORIA_CONVERSACION[chat_id] # borra contexto viejo
            return None
        
        # si no expiro le da contexto a lo demas
        return contexto['respuesta_bot']
    return None

@bot.message_handler(commands=["start", "help"])
def enviar_bienvenida(message):
    # se borra la memoria si el usuario usa /start o /help
    if message.chat.id in MEMORIA_CONVERSACION:
        del MEMORIA_CONVERSACION[message.chat.id]
    bot.reply_to(message, "¡Hola!, Soy MediBot, tu asistente de primeros auxilios. ¿Cuál es tu emergencia?")


@bot.message_handler(commands=["dea", "desfibrilador"])
def pedir_ubicacion_dea(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    boton_ubicacion = types.KeyboardButton("Compartir mi Ubicación 📍", request_location=True)
    markup.add(boton_ubicacion)
    
    bot.reply_to(message, 
        "Entendido. Para encontrar el DEA verificado más cercano, necesito tu ubicación actual.",
        reply_markup=markup
    )

@bot.message_handler(content_types=['location'])
def manejar_ubicacion_dea(message):
    lat_usuario = message.location.latitude
    lon_usuario = message.location.longitude
    chat_id = message.chat.id

    bot.send_chat_action(chat_id, 'typing')
    bot.reply_to(message, "Buscando DEA verificado más cercano en la base de datos de AWS...")

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
@bot.message_handler(func=lambda message: True)
def responder(message):
    if message.text is None:
        bot.reply_to(message, "Por favor, envíame tu consulta como un mensaje de texto.")
        return

    chat_id = message.chat.id
    pregunta = message.text

    # lee contexto si existe
    contexto_previo = _obtener_contexto(chat_id)
    
    if contexto_previo:
        bot.send_chat_action(chat_id, 'typing')
        # llama a groq para seguir en base al contexto
        respuesta_ia_groq = respuesta_groq_contextual(
            mensaje_usuario=pregunta,
            contexto_previo=contexto_previo
        )
        
        # formatea la respuesta (esto queda feo creo yo)
        respuesta_final = (
            f"_{respuesta_ia_groq}_"
        )
        
        bot.reply_to(message, respuesta_final, parse_mode="Markdown")
        
        # actualiza/guarda nuevo contexto
        MEMORIA_CONVERSACION[chat_id] = {
            "respuesta_bot": respuesta_ia_groq, # guarda la nueva respuesta
            "marca_tiempo": datetime.datetime.now()
        }
        return 

    # si no hay contexto, sigue normal
    
    analisis = transformer.analizar(pregunta)
    nivel_urgencia = analisis['nivel_urgencia']
    respuesta_base_ia = analisis['respuesta_ia']

    # decide accion en base a urgencia
    
    if nivel_urgencia == "ALTA":
        respuesta_dataset = responses.buscar_en_dataset(pregunta, dataset)
        
        if respuesta_dataset:
            # CASO 1
            respuesta_final = (
                f"🚨 **[EMERGENCIA]** 🚨\n"
                f"{respuesta_dataset}\n\n"
                f"-------------------------------------\n"
                f"⚠️ **ADVERTENCIA IMPORTANTE:** {respuesta_base_ia}"
            )
            bot.reply_to(message, respuesta_final, parse_mode="Markdown")
            # guarda contexto
            MEMORIA_CONVERSACION[chat_id] = {
                "respuesta_bot": respuesta_dataset,
                "marca_tiempo": datetime.datetime.now()
            }
        else:
            # CASO 2
            bot.send_chat_action(chat_id, 'typing') 
            respuesta_ia_groq = responses.respuesta_groq(pregunta)
            respuesta_final = (
                f"🚨 **[RESPUESTA GENERADA POR IA - EMERGENCIA]** 🚨\n"
                f"{respuesta_ia_groq}\n\n"
                f"-------------------------------------\n"
                f"⚠️ **ADVERTENCIA IMPORTANTE:** {respuesta_base_ia}"
            )
            bot.reply_to(message, respuesta_final, parse_mode="Markdown")
            # guarda contexto
            MEMORIA_CONVERSACION[chat_id] = {
                "respuesta_bot": respuesta_ia_groq,
                "marca_tiempo": datetime.datetime.now()
            }

    elif nivel_urgencia == "MEDIA" or nivel_urgencia == "MEDIA_NO_MEDICA":
        respuesta_dataset = responses.buscar_en_dataset(pregunta, dataset)
        
        if respuesta_dataset:
            # CASO 3
            respuesta_final = (
                f"🩺 **[RECOMENDACIÓN DE CUIDADO]** 🩹\n"
                f"{respuesta_dataset}\n\n"
                f"-------------------------------------\n"
                f"**Análisis Adicional:** {respuesta_base_ia}"
            )
            bot.reply_to(message, respuesta_final, parse_mode="Markdown")
            # ✨ GUARDAR CONTEXTO
            MEMORIA_CONVERSACION[chat_id] = {
                "respuesta_bot": respuesta_dataset,
                "marca_tiempo": datetime.datetime.now()
            }
        else:
            # CASO 4
            bot.send_chat_action(chat_id, 'typing')
            respuesta_ia_groq = responses.respuesta_groq(pregunta)
            respuesta_final = (
                f"🩺 **[ORIENTACIÓN POR IA - RECOMENDACIÓN DE CUIDADO]** 🩹\n"
                f"{respuesta_ia_groq}\n\n"
                f"-------------------------------------\n"
                f"**Análisis Adicional:** {respuesta_base_ia}"
            )
            bot.reply_to(message, respuesta_final, parse_mode="Markdown")
            # guarda contexto
            MEMORIA_CONVERSACION[chat_id] = {
                "respuesta_bot": respuesta_ia_groq,
                "marca_tiempo": datetime.datetime.now()
            }

    elif nivel_urgencia == "BAJA":
        if respuesta_base_ia == "INFO_NO_MEDICA_O_SALUDO":
            # CASO 5
            bot.send_chat_action(chat_id, 'typing')
            respuesta_ia_groq = responses.respuesta_groq(pregunta)
            bot.reply_to(message, respuesta_ia_groq)
            # guarda contexto
            MEMORIA_CONVERSACION[chat_id] = {
                "respuesta_bot": respuesta_ia_groq,
                "marca_tiempo": datetime.datetime.now()
            }
        else:
            # CASO 6
            respuesta_final = (
                f"✅ **ESTADO GENERAL BAJO RIESGO** 👍\n"
                f"*{respuesta_base_ia}*"
            )
            bot.reply_to(message, respuesta_final, parse_mode="Markdown")
            # guarda contexto
            MEMORIA_CONVERSACION[chat_id] = {
                "respuesta_bot": respuesta_base_ia,
                "marca_tiempo": datetime.datetime.now()
            }

    else: 
        # CASO 7: ERROR
        bot.send_chat_action(chat_id, 'typing')
        respuesta_ia_groq = responses.respuesta_groq(pregunta)
        respuesta_final = (
            f"🚫 **ERROR DE CLASIFICACIÓN** 🚫\n"
            f"Hemos encontrado una dificultad al clasificar su consulta. A continuación, se ofrece una respuesta generada por IA:\n"
            f"_{respuesta_ia_groq}_"
        )
        bot.reply_to(message, respuesta_final, parse_mode="Markdown")
        # guarda contexto
        MEMORIA_CONVERSACION[chat_id] = {
            "respuesta_bot": respuesta_ia_groq,
            "marca_tiempo": datetime.datetime.now()
        }

@bot.message_handler(content_types=['photo'])
def manejar_foto(mensaje):
    try:
        chat_id = mensaje.chat.id # chat_id
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
            
            # guarda contexto de la imagen
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
        bot.reply_to(message, "🎙️ Entendido. Transcribiendo tu audio, por favor espera...")

        texto_transcrito = transcribir_voz_con_groq(message)
        
        if not texto_transcrito:
            bot.reply_to(message, "Lo siento, no pude entender lo que dijiste en el audio. ¿Puedes intentarlo de nuevo o escribirlo?")
            return

        bot.reply_to(message, f"_[Has dicho]: {texto_transcrito}_ \n\nProcesando tu consulta...", parse_mode="Markdown")

        message.text = texto_transcrito
        
        responder(message) 
    
    except Exception as e:
        print(f"Error grave al procesar el audio: {e}")
        bot.reply_to(message, "Ocurrió un error inesperado al procesar tu audio.")

