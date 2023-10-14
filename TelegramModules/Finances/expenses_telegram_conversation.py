from typing import Awaitable
import datetime
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from Modules.Finances.expenses_data import Expenses
from Modules.Finances.expenses_commonutils import get_expenses, write_expense
from icecream import ic

actions_keyboard = [["Nuevo"], ["Editar", "Borrar"]]
edit_keyboard = ["Cantidad", "Razón", "Tag"]
confirm_keyboard = [["saltar"], ["terminar", "cancelar"]]

# region General


RECEIVE_EXPENSE, RECEIVE_TAG, RECEIVE_REASON = range(3)


def get_conversation_handler_expenses() -> ConversationHandler:
    ic("Creating handler for adding expenses")

    skip_filter = filters.Regex(r"^saltar$")
    cancel_filter = filters.Regex(r"^cancelar$")
    end_filter = filters.Regex(r"^terminar$")

    expense_message_handler = MessageHandler(filters.Regex(r"^\d+.?\d?$"), receive_expense)
    tag_message_handler = MessageHandler(filters.Regex(r"^\w+$") & ~skip_filter
                                         & ~cancel_filter & ~end_filter, receive_tag)
    reason_message_handler = MessageHandler(filters.TEXT & ~skip_filter & ~cancel_filter & ~end_filter, receive_reason)

    handler = ConversationHandler(
        entry_points=[CommandHandler("add", start_adding_expense)],
        states={
            RECEIVE_EXPENSE: [expense_message_handler],
            RECEIVE_TAG: [tag_message_handler, MessageHandler(skip_filter, ask_for_reason)],
            RECEIVE_REASON: [reason_message_handler, MessageHandler(skip_filter, ask_for_finish)]
        },
        fallbacks=[MessageHandler(cancel_filter, cancel_adding_expense),
                   MessageHandler(end_filter, ask_for_finish)]
    )

    return handler


# endregion

# region Adding Expense Conversation


session_expense: dict[int, Expenses] = {}


async def start_adding_expense(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ic("Adding expense conversation started")
    await update.message.reply_text("Por favor ingresa la cantidad a guardar")
    session_expense[update.effective_user.id] = Expenses(datetime.datetime.now())
    return RECEIVE_EXPENSE


async def receive_expense(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ic("Obtaining expense quantity")
    try:
        quantity = float(update.message.text)
        session_expense[update.effective_user.id].quantity = ic(quantity)
    except ValueError as e:
        # Probably should never happens since this is triggered with regex
        ic(e)
        await update.message.reply_text(f"Error inesperado al obtener el valor.\n{e}")
        return ConversationHandler.END
    return await ask_for_tag(update, context)


async def ask_for_tag(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ic("Waiting for expense's tag")
    await update.message.reply_text("Por favor ingresa el tag a guardar",
                                    reply_markup=ReplyKeyboardMarkup(confirm_keyboard, one_time_keyboard=True))
    return RECEIVE_TAG


async def receive_tag(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    ic("Obtaining expense tag")

    session_expense[user_id].tag = ic(context.match.string)

    return await ask_for_reason(update, context)


async def ask_for_reason(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ic("Waiting for expense's Reason")
    await update.message.reply_text("Por favor ingresa el motivo de este gasto",
                                    reply_markup=ReplyKeyboardMarkup(confirm_keyboard, one_time_keyboard=True))
    return RECEIVE_REASON


async def receive_reason(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    ic("Obtaining expense reason")
    session_expense[user_id].reason = update.message.text
    return await ask_for_finish(update, context)


async def ask_for_finish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ic("Finishing adding Expense")
    user_id = update.effective_user.id

    added_expense = ic(session_expense[user_id])

    save_session_expense(user_id)
    await update.message.reply_text(f"Se guardó el registro!\n{added_expense.get_user_repr()}")

    return ConversationHandler.END


async def cancel_adding_expense(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ic("User cancelled adding_expense conversation, expense NOT saved")
    await update.message.reply_text("Cancelaste el nuevo registro.")
    user_id = update.effective_user.id
    if user_id in session_expense:
        del session_expense[user_id]
    return ConversationHandler.END


def save_session_expense(user_id: int) -> None:
    ic("Saving Expense")
    if user_id not in session_expense:
        ic("wtf, user_id not in session for saving expense")
        return
    write_expense(user_id, session_expense[user_id])
    del session_expense[user_id]
# endregion
