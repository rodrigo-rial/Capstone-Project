import telebot as tbl
import os
import json
import difflib
from groq import Groq
from typing import Optional
import time
from dotenv import load_dotenv


#Cargar variables de entorno
load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', "") 
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "") 
GROQ_API_URL = 'https://api.groq.com/openai/v1/chat/completions' 
DATASET_PATH = 'primeros_auxilios.json'

if not TELEGRAM_TOKEN:
    raise ValueError("Porfavor, vuelva a intentar.")
if not GROQ_API_KEY:
    raise ValueError("Porfavor, vuelva a intentar.")

#Inicializar bot y cliente Groq 
bot = tbl.TeleBot(TELEGRAM_TOKEN)
groq_client = Groq(api_key=GROQ_API_KEY)


#Cargar dataset JSON
def load_company_data():
    try:
        with open("primeros_auxilios.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Error al cargar el JSON: {str(e)}")
        return None


company_data = load_company_data()


#Obtener respuesta del modelo (versión optimizada)
def get_groq_response(user_message: str) -> Optional[str]:
    try:
        # Buscar coincidencia más cercana en el dataset
        mejor_pregunta, mejor_respuesta = None, None
        mayor_similitud = 0

        for item in company_data:
            similitud = difflib.SequenceMatcher(None, user_message.lower(), item["pregunta"].lower()).ratio()
            if similitud > mayor_similitud:
                mayor_similitud = similitud
                mejor_pregunta, mejor_respuesta = item["pregunta"], item["respuesta"]

        if mayor_similitud < 0.4 or not mejor_respuesta:
            mejor_pregunta = "No se encontró una coincidencia directa."
            mejor_respuesta = (
                "⚠️ No tengo información específica sobre eso. "
                "Te recomiendo contactar con un profesional de la salud o "
                "llamar al 107 (SAME) si es urgente."
            )

        contexto = json.dumps(
            {"pregunta": mejor_pregunta, "respuesta": mejor_respuesta},
            ensure_ascii=False,
            indent=2,
        )

        system_prompt = f"""
Sos el asistente virtual de primeros auxilios 'MediBot Médico AI'.
Usá el siguiente contexto para ayudar al usuario:

{contexto}

Reglas:
- Si la consulta parece una emergencia (desmayo, sangrado abundante, dificultad respiratoria, convulsiones, dolor de pecho intenso),
  respondé con: '🚨 Esto puede ser una emergencia. Llamá urgente al 107 (SAME) o buscá ayuda médica profesional.'
- No recetes medicamentos ni hagas diagnósticos.
- Sé claro, empático y breve.
- Respondé siempre en español neutro.
"""

        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=400,
        )

        return chat_completion.choices[0].message.content.strip()

    except Exception as e:
        print(f"⚠️ Error al obtener la respuesta: {str(e)}")
        return None


#Transcripción de audio con Groq
def transcribe_voice_with_groq(message: tbl.types.Message) -> Optional[str]:
    try:
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        temp_file = "temp_voice.ogg"

        with open(temp_file, "wb") as f:
            f.write(downloaded_file)

        with open(temp_file, "rb") as file:
            transcription = groq_client.audio.transcriptions.create(
                file=(temp_file, file.read()),
                model="whisper-large-v3-turbo",
                prompt="El usuario describe una situación médica o emergencia.",
                response_format="json",
                language="es",
                temperature=0,
            )

        os.remove(temp_file)
        return transcription.text 

    except Exception as e:
        print(f"⚠️ Error al transcribir: {str(e)}")
        return None


#Comando start/help
@bot.message_handler(commands=["start", "help"])
def send_welcome(message: tbl.types.Message):
    if not company_data:
        bot.reply_to(message, "⚠️ Error al cargar la información. Por favor, intentá más tarde.")
        return

    bot.reply_to(
        message,
        "👋 ¡Hola! Soy el asistente de primeros auxilios. "
        "Enviame un mensaje de voz o texto  y te ayudaré con orientación básica 🩹.",
    )


#Manejar texto
@bot.message_handler(content_types=["text"])
def handle_text_message(message: tbl.types.Message):
    if not company_data:
        bot.reply_to(message, "⚠️ Error de diagnóstico. Intente más tarde.")
        return

    bot.send_chat_action(message.chat.id, "typing")

    response = get_groq_response(message.text)

    if response:
        bot.reply_to(message, response)
    else:
        bot.reply_to(
            message,
            "😕 No pude comprender lo que sucede. Por favor, buscá ayuda profesional o llamá al 107 (SAME).",
        )


#Manejar voz
@bot.message_handler(content_types=["voice"])
def handle_voice_message(message: tbl.types.Message):
    if not company_data:
        bot.reply_to(message, "⚠️ Error de diagnóstico. Intente de nuevo.")
        return

    bot.send_chat_action(message.chat.id, "typing")

    transcription = transcribe_voice_with_groq(message)

    if transcription:
        response = get_groq_response(transcription)
        if response:
            bot.reply_to(message, f"🗣️ *Transcripción:* {transcription}\n\n💬 {response}", parse_mode="Markdown")
        else:
            bot.reply_to(message, "⚠️ No pude obtener respuesta del asistente. Intenta nuevamente.")
    else:
        bot.reply_to(message, "⚠️ Error al transcribir el audio. Intenta nuevamente.")


#Ejecutar bot
if __name__ == "__main__":
    if company_data:
        print("🤖 MediBOT Bot de primeros auxilios iniciado correctamente✅")
        while True:
            try:
                bot.polling(none_stop=True, interval=0, timeout=20)
            except Exception as e:
                print(f"⚠️ Error en el bot: {str(e)}")
                print("Reiniciando el asistente de primeros auxilios...")
                time.sleep(5)
    else:
        print("❌ No se pudo cargar el dataset de primeros auxilios.")
