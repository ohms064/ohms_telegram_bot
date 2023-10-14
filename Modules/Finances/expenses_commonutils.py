# Common I/O functions to connect with expenses information
# to be used by other services like the commands for Telegram

from Modules.Finances.expenses_data import Expenses
import json
import os
from datetime import datetime
from icecream import ic
import dateutil.parser


def decode_time(target: dict):
    if 'time' in target:
        target["time"] = dateutil.parser.parse(target["time"])
        return target


def get_filename(user_id: int, month: int = 0, year: int = 0, date: datetime = None):
    if date is not None:
        month = date.month
        year = date.year
    return f"{user_id}_{month}_{year}_expenses.json"


def open_expenses_file(filename: str) -> list[Expenses]:
    result: list[Expenses] = []
    with open(filename, "r") as file:
        intermediate = json.load(file, object_hook=decode_time)
    for key in intermediate:
        result.append(Expenses(**key))
    return result


def get_expenses(user_id: int, month: int, year: int, tag: str = ""):
    ic(f"Getting expenses for {month}/{year}. With tag {tag}.")
    FILENAME = get_filename(user_id, month, year)
    result = []
    if not os.path.isfile(FILENAME):
        return result
    result = open_expenses_file(FILENAME)

    if tag:
        result = [e for e in result if e.tag == tag]

    return result


def write_expense(user_id: int, expense_to_write: Expenses):
    ic(f"Writing expense")
    FILENAME = get_filename(user_id, date=expense_to_write.time)
    expenses = get_expenses(user_id, expense_to_write.time.month, expense_to_write.time.year)
    expenses.append(expense_to_write)
    expenses = [exp.__dict__ for exp in expenses]

    with open(FILENAME, "w") as expense_file:
        json.dump(expenses, expense_file, default=str, indent=4, sort_keys=True)
