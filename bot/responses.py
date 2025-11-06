import requests
from config import GROQ_API_KEY, GROQ_API_URL

# stopwords (asi la busqueda en el dataset es mas especifica)
STOPWORDS = {
    "me", "se", "te", "le", "lo", "la", "el", "los", "las", "un", "una",
    "qué", "que", "como", "cómo", "dónde", "cuando", "por", "para", "con",
    "sin", "sobre", "de", "desde", "mi", "tu", "su", "tengo", "tienes",
    "estoy", "esta", "soy", "eres", "es", "somos", "son", "fue", "fui",
    "a", "o", "y", "del", "al", "mucho", "poco", "muy", "en", "si", "no"
}

def buscar_en_dataset(pregunta, dataset):
    pregunta_lower = pregunta.lower()
    palabras_usuario = set(palabra.strip(",.¿?¡!") for palabra in pregunta_lower.split() if palabra not in STOPWORDS)
    
    if not palabras_usuario or dataset is None:
        return None

    mejor_respuesta = None
    max_coincidencias = 0

    for item in dataset:
        pregunta_dataset_lower = item.get('pregunta', '').lower()
        coincidencias_actuales = 0
        
        for palabra_clave in palabras_usuario:
            if palabra_clave in pregunta_dataset_lower.split():
                coincidencias_actuales += 1
        
        if coincidencias_actuales > max_coincidencias:
            max_coincidencias = coincidencias_actuales
            mejor_respuesta = item.get('respuesta')

    return mejor_respuesta

def respuesta_groq(mensaje):
    if not GROQ_API_KEY or not GROQ_API_URL:
        print("Error: GROQ_API_KEY o GROQ_API_URL no están configuradas.")
        return "[Error de configuración de IA]"

    headers = {
        'Authorization': f'Bearer {GROQ_API_KEY}',
        'Content-Type': 'application/json'
    }

    SYSTEM_PROMPT = (
        "Eres Medibot, un asistente de primeros auxilios. Tu propósito es dar "
        "instrucciones claras y directas sobre cómo manejar una situación médica "
        "mientras llega la ayuda profesional. \n"
        "REGLAS IMPORTANTES:\n"
        "1. Prioriza la seguridad. Da pasos accionables y simples.\n"
        "2. NUNCA digas 'No soy un doctor' o 'No puedo dar consejo médico'. "
        "Tu rol es dar consejo de PRIMEROS AUXILIOS, no un diagnóstico.\n"
        "3. Sé conciso y ve al punto. Usa listas numeradas si es necesario.\n"
        "4. Asume que la situación es real y urgente.\n"
        "5. NUNCA intentes reemplazar la ayuda profesional. Tu respuesta debe ser "
        "un 'qué hacer ahora mismo'."
    )

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": mensaje}
        ],
        "temperature": 0.3
    }

    try:
        resp = requests.post(GROQ_API_URL, headers=headers, json=data, timeout=20)
        
        if resp.status_code == 200:
            respuesta = resp.json()['choices'][0]['message']['content']
            return respuesta.strip()
        else:
            print(f"Error en la API de Groq: {resp.status_code} - {resp.text}")
            return f"[Error Groq {resp.status_code}] No se pudo obtener respuesta."
    except Exception as e:
        print(f"Error de conexión a Groq: {e}")
        return f"[Error de conexión a Groq: {e}]"