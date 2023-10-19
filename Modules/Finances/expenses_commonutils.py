# Common I/O functions to connect with expenses information
# to be used by other services like the commands for Telegram
from json import JSONDecodeError

from Modules.Finances.expenses_data import Expenses
import json
import pytz
from datetime import datetime
from icecream import ic
import dateutil.parser
from firebase_admin import db


def decode_time(target: dict):
    if 'time' in target:
        target["time"] = dateutil.parser.parse(target["time"])
    return target


def get_filename(user_id: int, month: int = 0, year: int = 0, date: datetime = None):
    if date is not None:
        month = date.month
        year = date.year
    return f"users/{user_id}/expenses/{year}{month}"


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
    firebase_path = get_filename(user_id, month, year)
    firebase_ref = db.reference(firebase_path)

    if tag:
        firebase_ref = firebase_ref.order_by_child("tag").equal_to(tag)

    result = {}
    firebase_result = firebase_ref.get()
    for key in firebase_result:
        expenses_dict = firebase_result[key]
        result[key] = Expenses(time=datetime.fromisoformat(expenses_dict["time"]), quantity=expenses_dict["quantity"],
                               reason=expenses_dict["reason"], tag=expenses_dict["tag"])

    return result


def write_expense(user_id: int, expense_to_write: Expenses):
    ic(f"Writing expense")
    firebase_path = get_filename(user_id, date=expense_to_write.time)
    firebase_ref = db.reference(firebase_path)

    expense_dict = Expenses(**expense_to_write.__dict__)
    expense_dict.time = expense_to_write.time.isoformat()
    firebase_ref.push().update(expense_dict.__dict__)


def delete_expense(user_id: int, month: int, year: int, expense_id: str) -> None:
    firebase_path = get_filename(user_id, month, year)
    firebase_ref = db.reference(firebase_path)
    firebase_ref.child(expense_id).delete()
