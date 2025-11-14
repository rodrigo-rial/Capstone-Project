# 🩺 MediBot - Bot de Emergencias Médicas

Este bot de telegram brinda asistencia en emergencias médicas. Permite enviar mensajes de texto, audio o imágenes, y responde con primeros auxilios básicos hasta que llegue ayuda profesional.

## 📚 Contenidos
- [Características](#-características)
- [Instalación](#%EF%B8%8F-instalación)
- [Uso](#-uso)
- [Configuración](#%EF%B8%8F-configuración)
- [Contribuciones](#-contribuciones)
- [Autores](#%E2%80%8D-autores)
- [Enlaces útiles](#-enlaces-útiles)

## ✨ Características
MediBot cuenta con 5 funcionalidades importantes
- Procesa texto
- Procesa mensajes de voz
- Procesa imágenes
- Detecta el tono del mensaje enviado y analiza el sentimiento demostrado
- **Localizador de DEA:** Utiliza la ubicación del usuario para encontrar el Desfibrilador Externo Automático (DEA) verificado más cercano a través de una base de datos externa

A partir de la información brindada mediante texto, audio o imágenes, MediBot brinda instrucciones a seguir para poder actuar correctamente frente a emergencias.

## ⚙️ Instalación
1. **Clonar el repositorio**  
*En bash*  
git clone https://github.com/rodrigo-rial/Capstone-Project.git  
cd Capstone-Project

2. **Crear un entorno virtual**  
python -m venv entorno  
source entorno/Scripts/activate  
pip install -r requirements.txt  

3. **Crear un archivo *.env* con tus variables**  
TELEGRAM_TOKEN = tu_token  
GROQ_API_KEY = tu_api_key  

4. **Ejecutar el bot**  
python main.py

5. **Iniciar bot**  
/start

## 🚀 Uso
Una vez iniciado el bot, envia:
- /texto -> para describir una emergencia.
- /audio -> para enviar un mensaje de voz.
- /imagen -> para analizar una lesión via foto.
- /sentimientos -> para detectar sentimientos a través del mensaje.  
- **/dea -> para encontrar el Desfibrilador Externo Automático (DEA) más cercano.**  

O simplemente podrás hablar libremente con el bot sin necesidad de comandos. Tambíen cuenta con un menú de botones interactivos para mejor usabilidad.

## 🛠️ Configuración
Este proyecto utiliza variables de entorno en un archivo *.env*:
- TELEGRAM_TOKEN : Token del bot de Telegram
- GROQ_API_KEY : Clave para procesamiento de lenguaje
- URL_API_DEA : URL del servicio web (AWS API Gateway/Lambda) que usamos para la busqueda de DEAs

## 🤝 Contribuciones
¡Las contribuciones son bienvenidas!
Para colaborar:
1. Hacé un fork del repositorio
2. Creá una rama (git checkout -b feature/nueva-funcionalidad).
3. Subí tus cambios (git push origin feature/nueva-funcionalidad).
4. Abrí un Pull Request.  

También podes contribuir con ubicaciones donde se encuentren DEAs verificados: https://forms.gle/HZnwXW7ktdxF95wB7

## 👨‍💻 Autores
**Medibot** es parte del Proyecto Capstone del *Samsung Innovation Campus*, en alianza con *Fundación Mirgor* y alianza técnica con *Asociación Conciencia*.  
Dicho proyecto fue desarrollado por los siguientes integrantes del grupo **Coffee&Code**:
- Escobar Zoe
- Mazza Candela
- Rial Rodrigo

## 📝 Enlaces útiles
- [Documentación oficial de Groq API](https://console.groq.com/docs)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Documentación de Python](https://docs.python.org/3/)