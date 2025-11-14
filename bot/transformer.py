from transformers import pipeline
import json
import config

PALABRAS_URGENCIA_ALTA = config.PALABRAS_URGENCIA_ALTA
PALABRAS_URGENCIA_MEDIA = config.PALABRAS_URGENCIA_MEDIA
CONTACTO_EMERGENCIA_AR = config.CONTACTO_EMERGENCIA_AR

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

def clasificar_urgencia_por_palabras(frase: str) -> dict:
    frase_lower = frase.lower()
    nivel_urgencia = "BAJA"
    advertencia_ia = ""

    contiene_palabras_alta = any(palabra in frase_lower for palabra in PALABRAS_URGENCIA_ALTA)
    contiene_palabras_media = any(palabra in frase_lower for palabra in PALABRAS_URGENCIA_MEDIA)

    if contiene_palabras_alta:
        nivel_urgencia = "ALTA"
        advertencia_ia = f"¡Es una emergencia! {CONTACTO_EMERGENCIA_AR}"
    elif contiene_palabras_media:
        nivel_urgencia = "MEDIA"
        advertencia_ia = ("Entiendo tu preocupación. La siguiente información puede ayudarte. "
                          "**Recuerda consultar a un médico si el malestar persiste o empeora.**")
    else:
        nivel_urgencia = "BAJA"
        advertencia_ia = "Consulta informativa."

    return {
        "nivel_urgencia": nivel_urgencia,
        "advertencia_ia": advertencia_ia
    }

def analizar_sentimiento_texto(texto: str) -> dict:
    if ANALIZADOR_SENTIMIENTO is None:
        return {
            "sentimiento": "N/A",
            "confianza": 0.0,
            "error": "El modelo de análisis no está cargado."
        }

    try:
        resultado_sent = ANALIZADOR_SENTIMIENTO(texto)[0]
        sentimiento = resultado_sent['label']
        confianza = resultado_sent['score']
        
        return {
            "sentimiento": sentimiento,
            "confianza": confianza
        }
        
    except Exception as e: 
        print(f"Error en pipeline de sentimiento: {e}")
        return {
            "sentimiento": "N/A",
            "confianza": 0.0,
            "error": f"Error en pipeline: {e}"
        }
