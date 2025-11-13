import os

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '[TELEGRAM_TOKEN]')
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '[GROQ_API_KEY]')
GROQ_API_URL = 'https://api.groq.com/openai/v1/chat/completions'
DATASET_PATH = 'data/primeros_auxilios.json'

# palabras de alta severidad (esto lo pueden cambiar si quieren)

PALABRAS_URGENCIA_ALTA = {
    # emergencias
    "acv", "ataque", "infarto", "infartado", "parocardiaco", "no puedo respirar", 
    "dificultad respirar", "falta aire", "obstrucción", "pulmonar", "respirar", 
    "asfixia", "ahogo", "ahogando", "atragantamiento", "convulsión", "convulsionando", 
    "shock", "emergencia", "urgente", "anafilaxia", "anafiláctico", 
    
    # muerte y agonia
    "muero", "morir", "muere", "muerte", "moriré", "agonía", "moribundo", "muriendo", "agonizando",

    # sangrado
    "sangre", "sangrado", "desangrando", "sangrar", "hemorragia", "amputado", "cortado",
    "hemorragia interna",
    
    # trauma/golpes
    "golpe", "golpee", "golpeado", "fractura", "quebré", "quebrar", "accidente",
    "lesión", "columna", "craneal", "cabeza grave", "cuello", "médula", "ósea",
    
    # pérdida de conciencia 
    "desmayo", "desmayar", "perdio el conocimiento", "inconsciente", "síncope",
    "inconsciencia", "desvanecer",
    
    # dolor SEVERO
    "terrible", "muchísimo", "pecho", "insoportable", "crítico", "gravemente",
    "quemadura grave",
    
    # intoxicación y peligros externos
    "parto", "grave", "severo", "intenso", "veneno", "envenenamiento", "electrocución",
    "electrocutado", "rayo", "mordedura", "serpiente", "venenosas", "químicos",
    "explosión", "quemadura tercer grado"
}

PALABRAS_URGENCIA_MEDIA = {
    # dolor y malestar común
    "dolor", "duele", "cabeza", "dolor de cabeza", "punzada", "migraña",
    
    # sintomas generales
    "molestia", "incómodo", "preocupa", "malestar", "leve", "regular", "un poco",
    "mareo", "náuseas", "fiebre", "temperatura", "tengo tos", "tos", "estornudo", 
    "cansado", "gripe", "resfrío", "resfriado", "catarro", "ansiedad", "pánico",
    "vomito", "vómitos", "alergia", "picadura", "insecto", "erupción", "sarpullido",
    "quemadura", "esguince", "distensión", "tirón muscular", "torcedura",
    "moretón", "rasguño", "abrasión", "congestión", "garganta", "abdominal", 
    "estómago", "diarrea", "indigestión"
}

# umbral de confianza para considerar "alta confianza" en sentimientos negativos
UMBRAL_CONFIANZA_NEG = 0.80

# contactos de emergencia
CONTACTO_EMERGENCIA_AR = "Llame inmediatamente a la ambulancia (107), policía (911) o bomberos (100)."