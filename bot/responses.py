import requests
from config import GROQ_API_KEY, GROQ_API_URL
from rapidfuzz import fuzz

STOP_WORDS = set([
    "a", "al", "algo", "alguien", "alguno", "ante", "antes", "como", "con", 
    "contra", "cual", "cuando", "de", "del", "desde", "donde", "durante", 
    "e", "el", "ella", "ellas", "ello", "ellos", "en", "entre", "era", "es", 
    "esa", "ese", "eso", "esta", "estas", "este", "esto", "fue", "ha", "hace", 
    "hacer", "hacerle", "como", "cómo", "le", "tengo", "tienes", "tiene", "hasta", "hay", 
    "la", "las", "le", "les", "lo", "los", "me", "mi", "mis", "mucho", "muy", 
    "no", "nos", "nosotros", "o", "para", "pero", "por", "porque", "pues", 
    "que", "qué", "se", "sea", "sean", "ser", "si", "sí", "sin", "sino", 
    "sobre", "su", "sus", "te", "tu", "tus", "un", "una", "unas", "uno", "unos", 
    "y", "ya", "yo", "si", "siento", "estoy", "creo", "puedo"
])

def _limpiar_texto(texto: str) -> str:
    texto_limpio = ''.join(c for c in texto.lower() if c.isalnum() or c.isspace())
    tokens = [token for token in texto_limpio.split() if token not in STOP_WORDS]
    return " ".join(tokens)

def buscar_en_dataset(pregunta, dataset):
    mejor_respuesta = None
    mejor_similitud = 0
    
    pregunta_limpia = _limpiar_texto(pregunta)

    for item in dataset:
        pregunta_dataset = item.get("pregunta", "")
        pregunta_dataset_limpia = _limpiar_texto(pregunta_dataset)
        similitud = fuzz.token_set_ratio(pregunta_limpia, pregunta_dataset_limpia)

        if similitud > mejor_similitud:
            mejor_similitud = similitud
            mejor_respuesta = item.get("respuesta")

    if mejor_similitud >= 85:
        return mejor_respuesta

    return None

def respuesta_groq(mensaje):
    return respuesta_groq_contextual(mensaje_usuario=mensaje)

def respuesta_groq_contextual(mensaje_usuario, contexto_previo=None):
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
        "CONTEXTO: Fuiste creado para el curso de IA de Samsung por el grupo Coffee&Code (compuesto por Rodrigo, Candela y Zoe).\n\n"
        "REGLAS IMPORTANTES:\n"
        "1. Prioriza la seguridad. Da pasos accionables y simples.\n"
        "2. NUNCA digas 'No soy un doctor' o 'No puedo dar consejo médico'. "
        "Tu rol es dar consejo de PRIMEROS AUXILIOS, no un diagnóstico.\n"
        "3. Sé conciso y ve al punto. Usa listas numeradas si es necesario.\n"
        "4. Asume que la situación es real y urgente.\n"
        "5. NUNCA intentes reemplazar la ayuda profesional. Tu respuesta debe ser "
        "un 'qué hacer ahora mismo'."
    )
    
    mensajes = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    if contexto_previo:
        mensajes.append({"role": "assistant", "content": contexto_previo})
        
    mensajes.append({"role": "user", "content": mensaje_usuario})
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": mensajes,
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