# Common I/O functions to connect with expenses information
# to be used by other services like the commands for Telegram
from json import JSONDecodeError

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


def open_expenses_file(filename: str) -> dict[int, Expenses]:
    result: dict[int, Expenses] = {}
    with open(filename, "r", encoding="utf-8-sig") as file:
        try:
            intermediate = json.load(file, object_hook=decode_time)
        except JSONDecodeError as e:
            ic(f"Something weird happened: {e}")
            ic(file.read())
            return result

    if intermediate is None:
        ic(f"Something weird happened for {filename}")
        with open(filename, "r", encoding="utf-8-sig") as file:
            content = ic(file.read())
            ic(json.loads(content, object_hook=decode_time))
        return result
    for key, value in intermediate.items():
        result[key] = Expenses(**value)
    return result


def get_expenses(user_id: int, month: int, year: int, tag: str = "") -> dict[int, Expenses]:
    ic(f"Getting expenses for {month}/{year}. With tag {tag}.")
    FILENAME = get_filename(user_id, month, year)
    result = {}
    if not os.path.isfile(FILENAME):
        return result
    result = open_expenses_file(FILENAME)

    if tag:
        result = {key: value for key, value in result.items() if value.tag == tag}

    return result


def write_expense(user_id: int, expense_to_write: Expenses):
    ic(f"Writing expense")
    FILENAME = get_filename(user_id, date=expense_to_write.time)
    expenses = get_expenses(user_id, expense_to_write.time.month, expense_to_write.time.year)
    new_key = 1
    if len(expenses) != 0:
        new_key = max(list(expenses.keys())) + 1
    expenses[new_key] = expense_to_write
    expenses = {key: exp.__dict__ for key, exp in expenses.items()}

    with open(FILENAME, "w") as expense_file:
        json.dump(expenses, expense_file, default=str, indent=4, sort_keys=True)


def delete_expense(user_id: int, month: int, year: int, expense_id: int) -> None:
    filename = get_filename(user_id, month, year)
    expenses = get_expenses(user_id, month, year)
    if expense_id not in expenses:
        ic("Couldn't delete expense because it couldn't be found")
        return
    del expenses[expense_id]
    with open(filename, "w") as file:
        json.dump(expenses, file)
