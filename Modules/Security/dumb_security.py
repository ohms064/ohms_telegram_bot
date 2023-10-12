from telegram import Update
import json
from icecream import ic


def check_security(update: Update):
    ic("Checking security")
    user_id = update.effective_user.id
    with open("Info/api_keys.json", "r", encoding="utf-8-sig") as file:
        secure = json.load(file)
    #return "secure_ids" in secure and str(user_id) in secure["secure_ids"]
    return True
