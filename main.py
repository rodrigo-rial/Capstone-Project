import telebot as tlb
import requests
import json
import os

#  Carga de variables
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '[TELEGRAM_TOKEN]')
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '[API_KEY]')
GROQ_API_URL = '[GROQ_URL]'
DATASET_PATH = 'primeros_auxilios.json'

PALABRAS_EMERGENCIA = [
    "sangrado", "corte", "herida", "quemadura", "asfixia", "atragantamiento",
    "infarto", "desmayo", "convulsión", "epilepsia", "hipoglucemia", "shock",
    "ahogo", "picadura", "mordedura", "fractura", "golpe", "lesión"
]


def es_emergencia(mensaje):
    mensaje = mensaje.lower()
    return any(palabra in mensaje for palabra in PALABRAS_EMERGENCIA)


def cargar_dataset(DATASET_PATH):
    try:
        with open(DATASET_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
        
    except Exception as e:
        print(f"Error al cargar el json: {str(e)}")
        return None
    
# def buscar_en_dataset(pregunta, dataset):
#     pregunta = pregunta.strip().lower()
#     for item in dataset:
#         if item['pregunta'].strip().lower() == pregunta:
#             return item['respuesta']
#     return None

def buscar_en_dataset(pregunta, dataset):
    pregunta = pregunta.lower()
    for item in dataset:
        if any(palabra in pregunta for palabra in item['pregunta'].lower().split()):
            return item['respuesta']
    return None

# Respuesta general con IA
def respuesta_groq(mensaje):
    headers = {
        'Authorization': f'Bearer {GROQ_API_KEY}',
        'Content-Type': 'application/json'
    }

    system_prompt = f"""
     Eres un asistente virtual que puede responder cualquier tipo de pregunta.
    Si la pregunta es médica o de primeros auxilios, siempre indicá llamar a un profesional de salud o a emergencias (107 en Argentina).
    Responde de manera clara y breve, en español.
    """

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": mensaje}
        ],
    }

    try:
        resp = requests.post(GROQ_API_URL, headers=headers, json=data, timeout=20)
        if resp.status_code == 200:
            respuesta = resp.json()['choices'][0]['message']['content']
            return respuesta.strip()
        else:
            return f"[Error Groq {resp.status_code}]"
    except Exception as e:
        return f"[Erro de conexion a Groq: {e}]"


#  Instaciamos objetos de clase y cargamos el dataset
bot = tlb.TeleBot(TELEGRAM_TOKEN)
dataset = cargar_dataset(DATASET_PATH)

# Manejadores
@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(message, "¡Hola!, Soy tu asistente de primeros auxilios. ¿Cuál es tu emergencia?")

@bot.message_handler(func=lambda message: True)
def responder(message):
    pregunta = message.text

    if es_emergencia(pregunta):
        respuesta_dataset = buscar_en_dataset(pregunta, dataset)
        if respuesta_dataset:
            bot.reply_to(message, respuesta_dataset)
        else:
            bot.reply_to(message, "Parece una emergencia. LLamá al 107 o buscá ayuda médica inmediata.")
    else:
            respuesta_ia = respuesta_groq(pregunta)
            bot.reply_to(message, respuesta_ia)


# Punto de entrada (programa principal)
if __name__ == "__main__":
    print("Bot de Telegram de Primeros Auxilios iniciado. Esperando mensajes...")
    bot.infinity_polling()