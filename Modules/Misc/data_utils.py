from thefuzz import process

months_of_the_year = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
                      "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def month_to_int(month: str) -> int:
    result: int
    try:
        result = months_of_the_year.index(month) + 1
    except ValueError:
        result = -1
    return result


def fuzzy_month_to_int(month: str) -> int:
    result = process.extractOne(month, months_of_the_year)
    if result[1] < 50:
        return -1
    return month_to_int(result[0])


def int_to_month(month: int) -> str:
    if month < 0:
        return months_of_the_year[0]
    if month > len(months_of_the_year):
        return months_of_the_year[-1]
    return months_of_the_year[month]
