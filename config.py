import os

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '[TELEGRAM_TOKEN]')
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '[API_KEY]')
GROQ_API_URL = '[GROQ_URL]'
DATASET_PATH = 'data/primeros_auxilios.json' 

# palabras de alta severidad (esto lo pueden cambiar si quieren)

PALABRAS_URGENCIA_ALTA = {
    # emergencias vitales
    "acv", "ataque", "infarto", "parocardiaco", "no puedo respirar", "respirar", 
    "asfixia", "ahogo", "ahogando", "atragantamiento", "convulsión", "convulsionando", 
    "shock", "emergencia", "urgente", "anafilaxia", "anafiláctico", 
    
    # muerte
    "muero", "morir", "muere", "muerte", "moriré", "agonía",

    # sangrado
    "sangre", "sangrado", "desangrando", "sangrar", "hemorragia", "amputado",
    
    # trauma / golpes 
    "golpe", "golpee", "golpeado", "fractura", "quebre", "accidente",
    "lesión", "columna", "cuello", "médula",
    
    # pérdida de conciencia
    "desmayo", "desmayar", "perdio el conocimiento", "inconsciente", "síncope",
    
    # dolor SEVERO 
    "terrible", "muchísimo", "pecho", "insoportable",
    
    # otras cosas graves
    "parto", "grave", "severo", "intenso", "veneno", "envenenamiento", "electrocución",
    "electrocutado", "rayo", "mordedura", "serpiente"
}

PALABRAS_URGENCIA_MEDIA = {
    # dolor general o leve 
    "dolor", "duele", "cabeza", "dolor de cabeza", "muero",
    
    # malestar general
    "molestia", "incómodo", "preocupa", "malestar", "leve", "regular", "un poco",
    "mareo", "náuseas", "fiebre", "tengo tos", "tos", "estornudo", "cansado", 
    "gripe", "resfriado", "ansiedad", "vomito", "alergia", "picadura", "insecto",
    "quemadura", "esguince", "distensión", "moretón", "rasguño", "abrasión",
    "congestión", "garganta", "abdominal", "diarrea"
}

# umbral de confianza para considerar "alta confianza" en sentimientos negativos
UMBRAL_CONFIANZA_NEG = 0.80

# contactos de emergencia
CONTACTO_EMERGENCIA_AR = "Llame inmediatamente a la ambulancia (107), policía (911) o bomberos (100)."