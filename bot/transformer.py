from transformers import pipeline
import json
import config

# palabras clave (Se importan de config.py, donde deben estar definidas)
PALABRAS_URGENCIA_ALTA = config.PALABRAS_URGENCIA_ALTA
PALABRAS_URGENCIA_MEDIA = config.PALABRAS_URGENCIA_MEDIA
UMBRAL_CONFIANZA_NEG = config.UMBRAL_CONFIANZA_NEG
CONTACTO_EMERGENCIA_AR = config.CONTACTO_EMERGENCIA_AR # esto lo puse acá para que se pueda ir cambiando
# modelo
print("Cargando el modelo de análisis de sentimiento...")
try:
    ANALIZADOR_SENTIMIENTO = pipeline(
        "sentiment-analysis",
        model="pysentimiento/robertuito-sentiment-analysis"
    )
    print("Modelo cargado y listo")
except Exception as e:
    print(f"Error: No se pudo cargar el modelo de sentimiento: {e}")
    ANALIZADOR_SENTIMIENTO = None

# triaje (se fija severidad y da rta. en base a eso)
def _obtener_triaje(frase, sentimiento, confianza):

    frase_lower = frase.lower()
    nivel_urgencia = "BAJA"
    respuesta_ia = ""
    
    if sentimiento == "NEG":
        contiene_palabras_alta = any(palabra in frase_lower for palabra in PALABRAS_URGENCIA_ALTA)
        
        if contiene_palabras_alta and confianza > (UMBRAL_CONFIANZA_NEG * 0.5):
            # baje el requisito (de 0.8) porque sino hacia mucho problema con palabras cortas
            # p. ej. "me muero"
            nivel_urgencia = "ALTA"
            # incluye numeros de emergencia de arg.
            respuesta_ia = f"¡Es una emergencia! {CONTACTO_EMERGENCIA_AR}"
            
        elif any(palabra in frase_lower for palabra in PALABRAS_URGENCIA_MEDIA):
            nivel_urgencia = "MEDIA"
            # recomienda ir a un doctor

            respuesta_ia = "Entiendo tu preocupación. Te sugiero monitorear tus síntomas, descansar y **consultar a un médico si el malestar persiste o empeora.**"
            
        else:
            # caso de sentimiento NEG, pero sin palabras médicas (estoy triste, etc)
            # --- ESTO HAY QUE CHEQUEARLO ---
            nivel_urgencia = "MEDIA_NO_MEDICA" 
            respuesta_ia = "Lamento que te sientas mal. Si su malestar no es físico, hablemos de ello." 

    elif sentimiento == "NEU":
        # caso de sentimiento NEUTRAL (¿quien sos?, hola, gracias, cosas asi)
        nivel_urgencia = "BAJA"
        respuesta_ia = "INFO_NO_MEDICA_O_SALUDO" 
        
    elif sentimiento == "POS":
        nivel_urgencia = "BAJA"
        respuesta_ia = "¡Excelentes noticias! Me alegra saber que te sientes bien."
        
    else:
        nivel_urgencia = "INDETERMINADA"
        respuesta_ia = "No he podido determinar el nivel de urgencia."

    return nivel_urgencia, respuesta_ia

# función principal
def analizar(texto: str) -> dict:
    # devuelve analisis de sentimientos
    if ANALIZADOR_SENTIMIENTO is None:
        return {
            "frase": texto,
            "sentimiento": "N/A",
            "confianza": 0.0,
            "nivel_urgencia": "INDETERMINADA",
            "respuesta_ia": "Error: El modelo de análisis no está cargado."
        }

    # devuelve sentimiento base
    try:
        resultado_sent = ANALIZADOR_SENTIMIENTO(texto)[0]
        sentimiento = resultado_sent['label']
        confianza = resultado_sent['score']
        print(f"[DEBUG] modelo_label={sentimiento} score={confianza} texto='{texto}'")
    except Exception as e: 
        print(f"Error en pipeline de sentimiento: {e}")
        sentimiento = "N/A"
        confianza = 0.0

    # triaje
    nivel_urgencia, respuesta_ia = _obtener_triaje(texto, sentimiento, confianza)

    # devuelve JSON estructurado
    return {
        "frase": texto,
        "sentimiento": sentimiento,
        "confianza": confianza,
        "nivel_urgencia": nivel_urgencia,
        "respuesta_ia": respuesta_ia
    }