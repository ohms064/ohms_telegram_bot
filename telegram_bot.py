from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import json
from TelegramModules.Finances.expenses_telegram_commands import save_expense, load_expense
from TelegramModules.Finances.expenses_telegram_conversation import (get_conversation_handler_expenses_add, 
                                                                     get_conversation_handler_expenses_edit)
import os


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')

FILENAME = "Info/api_keys.json"
telegram_token = ""

if os.path.isfile(FILENAME):
    with open(FILENAME, "r", encoding="utf-8-sig") as api_keys_file:
        api_keys = json.load(api_keys_file)
        telegram_token = api_keys["api_id"]
else:
    telegram_token = os.getenv("telegram_key")

app = ApplicationBuilder().token(telegram_token).build()

app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler("gasto", save_expense))
app.add_handler(CommandHandler("leer", load_expense))
app.add_handler(get_conversation_handler_expenses_add())
app.add_handler(get_conversation_handler_expenses_edit())

app.run_polling()
