import requests
from config import GROQ_API_KEY, GROQ_API_URL

def buscar_en_dataset(pregunta, dataset):
    pregunta = pregunta.lower()
    for item in dataset:
        if any(palabra in pregunta for palabra in item['pregunta'].lower().split()):
            return item['respuesta']
    return None

def respuesta_groq(mensaje):
    headers = {
        'Authorization': f'Bearer {GROQ_API_KEY}',
        'Content-Type': 'application/json'
    }

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Tu prompt de sistema aquí..."},
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