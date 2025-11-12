import telebot as tlb
from config import TELEGRAM_TOKEN, DATASET_PATH
from bot import utils

bot = tlb.TeleBot(TELEGRAM_TOKEN, parse_mode="Markdown")

dataset = utils.cargar_dataset(DATASET_PATH)

MEMORIA_CONVERSACION = {}

if dataset is None:
    print("Advertencia: Dataset no cargado. El bot dependerá solo de la IA o lógica de emergencia.")