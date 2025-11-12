import datetime
from bot.bot_instance import bot, dataset, MEMORIA_CONVERSACION
from bot import utils, responses
from bot import transformer 
from bot.voz import transcribir_voz_con_groq 
from bot.vision import imagen_a_base64, describir_imagen_con_groq
from bot.responses import respuesta_groq_contextual
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

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

@bot.message_handler(commands=["start"])
def enviar_bienvenida(message):
    # se borra la memoria si el usuario usa /start o /help
    if message.chat.id in MEMORIA_CONVERSACION:
        del MEMORIA_CONVERSACION[message.chat.id]

    # Creamos botones y los agregamos al mensaje de bienvenida
    botones = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton("Analizar texto", callback_data="texto")
    btn2 = InlineKeyboardButton("Analizar voz", callback_data="voz")
    btn3 = InlineKeyboardButton("Analizar imagen", callback_data="imagen")
    btn4 = InlineKeyboardButton("Analizar Sentimiento", callback_data="sentimiento")
    btn5 = InlineKeyboardButton("🛈 Acerca de mi", callback_data="acerca")
    btn6 = InlineKeyboardButton("Ayuda", callback_data="ayuda")
    botones.add(btn1, btn2, btn3, btn4, btn5, btn6)
    bot.reply_to(message, "🤖 ¡Hola!, Soy MediBot, tu asistente de primeros auxilios. ¿Cuál es tu emergencia?", reply_markup = botones)

# Manejador de botones
@bot.callback_query_handler(func=lambda call:True)
def callback(call):
    bot.answer_callback_query(call.id)

    # Opción texto
    if call.data == "texto":    
        bot.send_message(
            call.message.chat.id,
            "*TEXTO* \n\n"
            "🩺 Contame por *texto* tu emergencia y te brindo la información necesaria para actuar correctamente hasta que llegue ayuda profesional! "
        )
        
    elif call.data == "voz":
        bot.send_message(
            call.message.chat.id,
            "*AUDIO* \n\n"
            "🎙️ Por favor, enviá un *audio* contando tu emergencia. Con esa información voy a guiarte paso a paso con las indicaciones de primeros auxilios más adecuadas."
        )
            
    elif call.data == "imagen":
        bot.send_message(
            call.message.chat.id,
            "*IMAGEN* \n\n"
            "📸 Enviá una *imagen clara* de la herida o la zona afectada. Con esa información puedo analizarla y orientarte sobre el tipo de lesión y los primeros auxilios recomendados."
        )
            
    elif call.data == "sentimiento":
        bot.send_message(
            call.message.chat.id,
            "*SENTIMIENTOS* \n\n"
            "🧠 Enviá un *mensaje de voz o texto* contándome cómo te sentís, así puedo analizar tu tono emocional y ofrecerte orientación o contención si lo necesitás."
        )
            
    elif call.data == "acerca":
        bot.send_message(
            call.message.chat.id,
            "*ACERCA DE MI* \n\n"
            "🤖 Soy *MediBot*, tu asistente de primeros auxilios desarrollado por el equipo *Coffe&Code* del *Samsung Innovation Campus*. Estoy diseñado para orientarte ante emergencias leves, brindando información rápida y confiable. 🚑"
        )

    elif call.data == "ayuda":
        bot.send_message(
            call.message.chat.id,
            "ℹ️ Puedo ayudarte de distintas formas:\n\n"
            "- 📄 Recibir emergencias por texto.\n"
            "- 🎙️ Analizar audios para guiarte paso a paso.\n"
            "- 📸 Identificar heridas mediante imágenes.\n"
            "- 💬 Analizar el tono emocional de tu mensaje.\n\n"
            "Podés reiniciar la conversación en cualquier momento enviando */start*.\n\n"
            "*Comandos*\n"
            "- */texto*\n"
            "- */imagen*\n"
            "- */sentimientos*\n"
            "- */ayuda* o */help*"
        )

        
# Manejador para comandos de ayuda
@bot.message_handler(commands=["texto", "audio", "imagen", "sentimientos", "ayuda", "help"])
def enviar_ayuda(message):
    comando = message.text.lower()
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
            
    elif comando == "/sentimientos":
        bot.reply_to(
            message,
            "*SENTIMIENTOS* \n\n"
            "🧠 Enviá un *mensaje de voz o texto* contándome cómo te sentís, así puedo analizar tu tono emocional y ofrecerte orientación o contención si lo necesitás."
        )
        
    elif comando in ["/ayuda", "/help"]:
        bot.reply_to(
            message,
            "ℹ️ Puedo ayudarte de distintas formas:\n\n"
            "- 📄 Recibir emergencias por texto.\n"
            "- 🎙️ Analizar audios para guiarte paso a paso.\n"
            "- 📸 Identificar heridas mediante imágenes.\n"
            "- 💬 Analizar el tono emocional de tu mensaje.\n\n"
            "Podés reiniciar la conversación en cualquier momento enviando */start*.\n\n"
            "*Comandos*\n"
            "- */texto*\n"
            "- */imagen*\n"
            "- */sentimientos*\n"
            "- */ayuda* o */help*"
        )
    

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