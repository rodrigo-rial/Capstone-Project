import os
from groq import Groq
from typing import Optional
import telebot as tbl 
from bot.bot_instance import bot 
from config import GROQ_API_KEY 

cliente_groq = Groq(api_key=GROQ_API_KEY)

def transcribir_voz_con_groq(message: tbl.types.Message) -> Optional[str]:
    
    if cliente_groq is None:
        print("⚠️ Error: El cliente Groq no está inicializado.")
        return None
            
    try:
        info_archivo = bot.get_file(message.voice.file_id)
        archivo_descargado = bot.download_file(info_archivo.file_path)
        archivo_temporal = "temp_voice.ogg"

        with open(archivo_temporal, "wb") as archivo_local:
            archivo_local.write(archivo_descargado)

        with open(archivo_temporal, "rb") as archivo_audio:
            transcripcion = cliente_groq.audio.transcriptions.create(
                file=(archivo_temporal, archivo_audio.read()),
                model="whisper-large-v3-turbo",
                prompt="El usuario describe una situación médica o emergencia.",
                response_format="json",
                language="es",
                temperature=0,
            )

        os.remove(archivo_temporal)
        
        return transcripcion.text

    except Exception as e:
        print(f"⚠️ Error al transcribir: {str(e)}")
        return None