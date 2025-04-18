from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
import json
from TelegramModules.Finances.expenses_telegram_commands import save_expense, load_expense
from TelegramModules.Finances.expenses_telegram_conversation import (get_conversation_handler_expenses_add, 
                                                                     get_conversation_handler_expenses_edit)
import os
from TelegramModules.Finances.expenses_telegram_utils import button_query_handler
import firebase_admin


FIREBASE_DB_URL = "https://telegramohmsbot-default-rtdb.firebaseio.com/"
FIREBASE_KEYS_PATH = "Info/firebase_key.json"

API_KEYS_PATH = "Info/api_keys.json"
telegram_token = ""

cred = firebase_admin.credentials.Certificate(FIREBASE_KEYS_PATH)
firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_DB_URL})

telegram_token: str

if os.path.isfile(API_KEYS_PATH):
    with open(API_KEYS_PATH, "r", encoding="utf-8-sig") as api_keys_file:
        api_keys = json.load(api_keys_file)
        telegram_token = api_keys["api_id"]

if not telegram_token:
    telegram_token = os.getenv("telegram_key")

app = ApplicationBuilder().token(telegram_token).arbitrary_callback_data(True).build()

app.add_handler(CommandHandler("gasto", save_expense))
app.add_handler(CommandHandler("leer", load_expense))
app.add_handler(get_conversation_handler_expenses_add())
app.add_handler(get_conversation_handler_expenses_edit())
app.add_handler(CallbackQueryHandler(button_query_handler))

app.run_polling()
