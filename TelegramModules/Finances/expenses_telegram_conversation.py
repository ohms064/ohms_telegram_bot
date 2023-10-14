import datetime
from Modules.Misc.data_utils import fuzzy_month_to_int, int_to_month
from dateutil import relativedelta
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from Modules.Finances.expenses_data import Expenses
from Modules.Finances.expenses_commonutils import get_expenses, write_expense
from icecream import ic

actions_keyboard = [["Nuevo"], ["Editar", "Borrar"]]
edit_keyboard = ["Cantidad", "Razón", "Tag"]
confirm_keyboard = [["saltar"], ["terminar", "cancelar"]]

# region General


RECEIVE_EXPENSE, RECEIVE_TAG, RECEIVE_REASON, RECEIVE_DATE, SUM_RESULT = range(5)

skip_filter = filters.Regex(r"^saltar$")
cancel_filter = filters.Regex(r"^cancelar$")
end_filter = filters.Regex(r"^terminar$")
tag_filter = filters.Regex(r"^\w+$")
number_filter = filters.Regex(r"^\d+.?\d?$")


def get_conversation_handler_expenses_add() -> ConversationHandler:
    ic("Creating handler for adding expenses")
    expense_message_handler = MessageHandler(number_filter, receive_expense_builder(ask_for_tag_builder(RECEIVE_TAG)))
    tag_message_handler = MessageHandler(tag_filter & ~skip_filter
                                         & ~cancel_filter
                                         & ~end_filter, receive_tag_builder(ask_for_reason_builder(RECEIVE_REASON)))
    reason_message_handler = MessageHandler(filters.TEXT & ~skip_filter & ~cancel_filter & ~end_filter,
                                            receive_reason_builder(ask_for_add_finish))

    handler = ConversationHandler(
        entry_points=[CommandHandler("add", start_creating_expense)],
        states={
            RECEIVE_EXPENSE: [expense_message_handler],
            RECEIVE_TAG: [tag_message_handler, MessageHandler(skip_filter, ask_for_reason_builder(RECEIVE_REASON))],
            RECEIVE_REASON: [reason_message_handler, MessageHandler(skip_filter, ask_for_add_finish)]
        },
        fallbacks=[MessageHandler(cancel_filter, cancel_process),
                   MessageHandler(end_filter, ask_for_add_finish)]
    )

    return handler


def get_conversation_handler_expenses_edit() -> ConversationHandler:
    tag_message_handler = MessageHandler(tag_filter & ~skip_filter
                                         & ~cancel_filter
                                         & ~end_filter, receive_tag_builder(ask_for_reason_builder(RECEIVE_DATE)))
    return ConversationHandler(
        entry_points=[CommandHandler("get", start_getting_expenses)],
        states={
            RECEIVE_TAG: [tag_message_handler],
            RECEIVE_DATE: [],
        },
        fallbacks=[MessageHandler(cancel_filter, cancel_process)]
    )


async def cancel_process(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    ic(f"User: {user_id} cancelled process, expense NOT saved")
    await update.message.reply_text("Cancelado.")
    end_session_expense(user_id)
    return ConversationHandler.END
# endregion


# region Session Actions
# Ugly? Have a feeling that this can be added to context somehow
session_expense: dict[int, Expenses] = {}


def start_session(user_id: int) -> None:
    session_expense[user_id] = Expenses(datetime.datetime.now())


def update_session_quantity(user_id: int, quantity: float) -> None:
    session_expense[user_id].quantity = quantity


def update_session_tag(user_id: int, tag: str) -> None:
    session_expense[user_id].tag = tag


def update_session_reason(user_id: int, reason: str) -> None:
    session_expense[user_id].reason = reason


def update_session_date(user_id: int, day: int = -1, month: int = -1, year: int = -1) -> None:
    delta = relativedelta.relativedelta()
    if day != -1:
        delta.day = day
    if month != -1:
        delta.month = month
    if year != -1:
        delta.year = year
    session_expense[user_id].time += delta


def save_session_expense(user_id: int) -> None:
    ic("Saving Expense")
    if user_id not in session_expense:
        ic("wtf, user_id not in session for saving expense")
        return
    write_expense(user_id, session_expense[user_id])
    end_session_expense(user_id)


def end_session_expense(user_id):
    if user_id in session_expense:
        del session_expense[user_id]
# endregion


# region Data Receivers
# Requires regex for safe activation
def receive_expense_builder(callback):
    async def receive_expense(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        ic("Obtaining expense quantity")
        user_id = update.effective_user.id
        try:
            quantity = float(context.match.string)
            update_session_quantity(user_id, ic(quantity))
        except ValueError as e:
            # Probably should never happens since this is triggered with regex
            ic(e)
            await update.message.reply_text(f"Error inesperado al obtener el valor.\n{e}")
            return ConversationHandler.END
        return await callback(update, context)
    return receive_expense


# Requires regex for safe activation
def receive_tag_builder(callback):
    async def receive_tag(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        ic("Obtaining expense tag")
        user_id = update.effective_user.id
        update_session_tag(user_id, ic(context.match.string))
        return await callback(update, context)
    return receive_tag


def receive_reason_builder(callback):
    async def receive_reason(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_id = update.effective_user.id
        ic("Obtaining expense reason")
        update_session_reason(user_id, update.message.text)
        return await callback(update, context)
    return receive_reason


# Probably not going to use it
def receive_day_builder(callback, state_if_error: int):
    async def receive_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_id = update.effective_user.id
        result = ic(parse_day(context.match.string))

        if result == -1:
            return await ask_for_date_builder(state_if_error)(update, context)

        update_session_date(user_id, day=result)
        return await callback(update, context)
    return receive_date


def receive_month_builder(callback, state_if_error: int):
    async def receive_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_id = update.effective_user.id
        result = ic(parse_month(context.match.string))

        if result == -1:
            return await ask_for_date_builder(state_if_error)(update, context)

        update_session_date(user_id, month=result)
        return await callback(update, context)
    return receive_date


def receive_year_builder(callback, state_if_error: int):
    async def receive_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_id = update.effective_user.id
        result = ic(parse_year(context.match.string))

        if result == -1:
            return await ask_for_date_builder(state_if_error)(update, context)

        update_session_date(user_id, year=result)
        return await callback(update, context)
    return receive_date


# Probably not going to use it
def receive_day_month_builder(callback, state_if_error: int):
    async def receive_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_id = update.effective_user.id
        day, month = context.match.string.split()
        result_day = ic(parse_day(day))
        result_month = ic(parse_month(month))

        if result_day == -1 or result_month == -1:
            return await ask_for_date_builder(state_if_error)(update, context)

        update_session_date(user_id, day=result_day, month=result_month)
        return await callback(update, context)
    return receive_date


def receive_month_year_builder(callback, state_if_error: int):
    async def receive_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_id = update.effective_user.id
        month, year = context.match.string.split()
        result_month = ic(parse_month(month))
        result_year = ic(parse_day(year))

        if result_year == -1 or result_month == -1:
            return await ask_for_date_builder(state_if_error)(update, context)

        update_session_date(user_id, year=result_year, month=result_month)
        return await callback(update, context)
    return receive_date


def receive_day_month_year_builder(callback, state_if_error: int):
    async def receive_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_id = update.effective_user.id
        day, month, year = context.match.string.split()
        result_day = ic(parse_day(day))
        result_month = ic(parse_month(month))
        result_year = ic(parse_day(year))

        if result_year == -1 or result_day == -1 or result_month == -1:
            return await ask_for_date_builder(state_if_error)(update, context)

        update_session_date(user_id, day=result_day, month=result_month, year=result_year)
        return await callback(update, context)
    return receive_date
# endregion


# region Data Requesters
def ask_for_quantity_builder(state_to_return: int):
    async def ask_for_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        ic("Adding expense conversation started")
        user_id = update.effective_user.id
        await update.message.reply_text("Por favor ingresa la cantidad")
        start_session(user_id)
        return state_to_return
    return ask_for_quantity


def ask_for_tag_builder(state_to_return: int):
    async def ask_for_tag(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        ic("Waiting for expense's tag")
        await update.message.reply_text("Por favor ingresa el tag a guardar",
                                        reply_markup=ReplyKeyboardMarkup(confirm_keyboard, one_time_keyboard=True))
        return state_to_return
    return ask_for_tag


def ask_for_reason_builder(state_to_return: int):
    async def ask_for_reason(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        ic("Waiting for expense's Reason")
        await update.message.reply_text("Por favor ingresa el motivo de este gasto",
                                        reply_markup=ReplyKeyboardMarkup(confirm_keyboard, one_time_keyboard=True))
        return state_to_return
    return ask_for_reason


def ask_for_date_builder(state_to_return: int):
    async def ask_for_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        ic("Waiting for expense's Date")
        await update.message.reply_text(
            "Por favor ingresa la fecha. Puedes ingresar el día, mes con nombre o número y "
            "el año separado por un espacio de la siguiente forma 'dd mm' 'mm aaaa' 'dd mm aaaa'.")
        return state_to_return
    return ask_for_date
# endregion


# region Adding Expense Conversation
async def start_creating_expense(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    ic(f"Starting creating expense process for user {user_id}")
    start_session(user_id)
    await update.message.reply_text(f"Iniciamos el proceso para un nuevo gasto")
    return await ask_for_quantity_builder(RECEIVE_EXPENSE)(update, context)


async def ask_for_add_finish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    ic(f"Ending creating expense process for user: {user_id}")

    added_expense = ic(session_expense[user_id])

    save_session_expense(user_id)
    await update.message.reply_text(f"Se guardó el registro!\n{added_expense.get_user_repr()}")

    return ConversationHandler.END
# endregion


# region Edit Expense Conversation
async def start_getting_expenses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    ic(f"User: {user_id} started process of retrieving expenses")
    start_session(user_id)
    return CONFIGURE_TAG
# endregion


# region Date Parser

def parse_day(day: str):
    result: int
    try:
        result = int(day)
        if 31 < result < 0:
            result = -1
    except ValueError:
        result = -1
    return result


def parse_month(month: str):
    result: int
    try:
        result = int(month)
        if 12 < result < 1:
            result = -1
    except ValueError:
        result = fuzzy_month_to_int(month)
    return result


def parse_year(year: str):
    result: int
    try:
        result = int(year)
        if result < 1000:
            result = -1
    except ValueError:
        result = -1
    return result
# endregion
