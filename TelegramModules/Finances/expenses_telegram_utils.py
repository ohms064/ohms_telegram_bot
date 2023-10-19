from telegram import InlineKeyboardButton, Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import json
from Modules.Finances.expenses_commonutils import delete_expense


DELETE_ACTION = 1


def create_expense_keyboard_markup(user_id: int, month: int, year: int, expense_id: str) -> InlineKeyboardMarkup:
    keyboard = [
        [
            create_delete_button(user_id, month, year, expense_id)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_delete_button(user_id: int, month: int, year: int, expense_id: str) -> InlineKeyboardButton:
    action = create_query_action(DELETE_ACTION, user_id=user_id, month=month, year=year, expense_id=expense_id)
    return InlineKeyboardButton("Borrar", callback_data=json.dumps(action))


async def button_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    query_action = json.loads(query.data)
    action = query_action["action"]
    del query_action["action"]
    if action == DELETE_ACTION:
        delete_expense(**query_action)

    await query.edit_message_text(text="Borrado")
    await query.answer()


def create_query_action(action: int, **kwargs) -> dict:
    action = {"action": action}
    action.update(kwargs)
    return action
