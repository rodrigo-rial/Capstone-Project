from PIL import Image
from groq import Groq
import base64
from config import GROQ_API_KEY



cliente_groq = Groq(api_key=GROQ_API_KEY)

# Funcion para convertir a b64
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

# Función para describir imagen con Groq
def describir_imagen_con_groq(imagen_base64):
    try:
        completado_chat = cliente_groq.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content":[
                        {
                            "type": "text",
                            "text": "Por favor, simula que eres un asistente de primeros auxilios y debes sugerir una respuesta en español a la imagen. Sé claro y profesional",
                            "image_url":{
                                "url": f"data:image/jpeg;base64,{imagen_base64}"
                            }
                        }
                    ]
                }
            ],
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            temperature=0.7,
            max_tokens=2000
        )
        return completado_chat.choices[0].message.content
    
    except Exception as e:
        print(f"Error al describir imagen con Groq: {e}")
        return None

# Manejador de Fotos
@bot.message_handler(content_types=['photo'])
def manejar_foto(mensaje):
    try:
        bot.reply_to(mensaje, "He recibido tu imagen. Analizandola...")
        foto = mensaje.photo[-1]
        info_archivo = bot.get_file(foto.file_id)
        archivo_descargado = bot.download_file(info_archivo.file_path)
        imagen_base64 = imagen_a_base64(archivo_descargado)

        if not imagen_a_base64:
            bot.reply_to(mensaje, "Error al procesar la imagen. Intenta de nuevo")
            return
        
        descripcion = describir_imagen_con_groq(imagen_base64)
        if descripcion:
            bot.reply_to(mensaje, descripcion, parse_mode='Markdown')
        else:
            bot.reply_to(mensaje, "No pude analizar la imagen. Por favor intenta con otra")
    
    except Exception as e:
        print(f"Error al procesar la imagen: {e}")
        bot.reply_to(mensaje, "Ocurrió un error al procesar tu imagen. Intenta de nuevo")
