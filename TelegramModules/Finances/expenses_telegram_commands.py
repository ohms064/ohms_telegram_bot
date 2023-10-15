import datetime
from dateutil import relativedelta
from telegram import Update
from telegram.ext import ContextTypes
from TelegramModules.Security.dumb_security import check_security
from Modules.Finances.expenses_data import Expenses
from Modules.Finances.expenses_commonutils import get_expenses, write_expense
from icecream import ic


async def save_expense(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ic("Saving new expense")
    secure = check_security(update)

    if not secure:
        return

    if len(context.args) == 0:
        return

    date = datetime.datetime.now()
    user_id = update.effective_user.id

    # TODO:
    # Kinda ugly, would like to have a separate way to get an Expense from a message
    # but this is the only instance so maybe it's not worth it

    new_expense = Expenses(time=date)
    new_expense.time = date
    try:
        new_expense.quantity = float(context.args[0])
    except ValueError:
        await update.effective_message.reply_text(f"El valor {context.args[0]} no es un número correcto")
        return

    if len(context.args) > 1:
        new_expense.tag = context.args[1]

    if len(context.args) > 2:
        reason = " "
        new_expense.reason = reason.join(context.args[2:])

    if new_expense.quantity < 0:
        new_expense.quantity *= -1

    # Ugliness ends

    write_expense(user_id, new_expense)

    await update.effective_message.reply_text(f"Se agregó el gasto: {new_expense.get_user_repr()}")


async def load_expense(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ic("Loading expenses")
    tag = ""
    date = datetime.datetime.now()
    user_id = update.effective_user.id

    secure = check_security(update)
    if not secure:
        return

    if len(context.args) > 0:
        tag = context.args[0]

    result = {}

    expenses = get_expenses(user_id, date.month, date.year, tag)
    result[f"{date.month}_{date.year}"] = expenses
    while len(expenses) > 0:
        date += relativedelta.relativedelta(months=1)
        expenses = get_expenses(user_id, date.month, date.year, tag)
        result[f"{date.month}_{date.year}"] = expenses
    for monthly_key, month_expenses in result.items():
        for expense_key, expense in month_expenses.items():
            pretty = result[monthly_key][expense_key].get_user_repr()
            await update.effective_message.reply_text(f"Éstos son los gastos: \n{pretty}")


async def save_expense_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ic("Saving new expense")
    secure = check_security(update)

    if not secure:
        return

    if len(context.args) == 0:
        return

    date = datetime.datetime.now()
    user_id = update.effective_user.id

    # TODO:
    # Kinda ugly, would like to have a separate way to get an Expense from a message
    # but this is the only instance so maybe it's not worth it

    new_expense = Expenses(time=date)
    new_expense.time = date
    try:
        new_expense.quantity = float(context.args[0])
    except ValueError:
        await update.effective_message.reply_text(f"El valor {context.args[0]} no es un número correcto")
        return

    if len(context.args) > 1:
        new_expense.tag = context.args[1]

    if len(context.args) > 2:
        reason = " "
        new_expense.reason = reason.join(context.args[2:])

    if new_expense.quantity < 0:
        new_expense.quantity *= -1

    # Ugliness ends

    write_expense(user_id, new_expense)

    await update.effective_message.reply_text(f"Se agregó el gasto: {new_expense.get_user_repr()}")
