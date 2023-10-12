from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import json
from Modules.Finances.expenses_telegram_commands import save_expense, load_expense

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')

with open("Info/api_keys.json", "r", encoding="utf-8-sig") as api_keys_file:
    api_keys = json.load(api_keys_file)

app = ApplicationBuilder().token(api_keys["api_id"]).build()

app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler("gasto", save_expense))
app.add_handler(CommandHandler("leer", load_expense))

app.run_polling()
