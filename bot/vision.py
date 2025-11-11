from PIL import Image
from groq import Groq
import base64
from config import GROQ_API_KEY

cliente_groq = Groq(api_key=GROQ_API_KEY)

def imagen_a_base64(ruta_o_bytes_imagen):
    try:
        if isinstance(ruta_o_bytes_imagen, bytes):
            return base64.b64encode(ruta_o_bytes_imagen).decode('utf-8')
        else:
            with open(ruta_o_bytes_imagen, "rb") as archivo_imagen:
                return base64.b64encode(archivo_imagen.read()).decode('utf-8')
    except Exception as e:
        print(f"Error al convertir imagen a base64: {e}")
        return None

def describir_imagen_con_groq(imagen_base64):
    try:
        completado_chat = cliente_groq.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{imagen_base64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": (
                                "Actúa como asistente de primeros auxilios. "
                                "Describe lo que ves en la imagen y da recomendaciones claras, "
                                "seguras y en español."
                            )
                        }
                    ]
                }
            ],
            max_tokens=800
        )

        return completado_chat.choices[0].message.content
    
    except Exception as e:
        print(f"Error al describir imagen con Groq: {e}")
        return None