import os

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '[TELEGRAM_TOKEN]')
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '[API_KEY]')
GROQ_API_URL = '[GROQ_URL]'
DATASET_PATH = 'primeros_auxilios.json'

DATASET_PATH = 'data/primeros_auxilios.json' 

PALABRAS_EMERGENCIA = [
    "sangrado", "corte", "herida", "quemadura", "asfixia", "atragantamiento",
    "infarto", "desmayo", "convulsión", "epilepsia", "hipoglucemia", "shock",
    "ahogo", "picadura", "mordedura", "fractura", "golpe", "lesión"
]