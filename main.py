
from bot.bot_instance import bot
from bot import handlers 

if __name__ == "__main__":
    print("Bot de Telegram de Primeros Auxilios iniciado. Esperando mensajes...")
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"Error fatal en el polling: {e}")
