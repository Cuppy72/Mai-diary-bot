from datetime import date

from telebot import types

now_day = date.today().day
now_month = date.today().month
now_year = date.today().year

current_day = now_day
current_month = now_month
current_year = now_year

name_of_day = {0: "Понедельник", 1: "Вторник", 2: "Среда", 3: "Четверг", 4: "Пятница", 5: "Суббота", 6: "Воскресенье"}

weeks_dict = {}


def create_button(current_date):
    if str(current_date) not in weeks_dict:
        button = types.InlineKeyboardButton(text=f"{name_of_day[current_date.weekday()]} - "
                                                 f"{str(current_date.day).rjust(2, '0')}."
                                                 f"{str(current_date.month).rjust(2, '0')}",

                                            callback_data=str(current_date))
        weeks_dict.update({str(current_date): button})

        return button
    else:
        return weeks_dict[str(current_date)]


def current_date_valid(day, month, year):
    try:
        current_date = date(year, month, day)
        return current_date

    except ValueError:
        return False


def date_decrease(day, month):
    global current_year
    day -= 1
    if day < 1:
        day = 31
        month -= 1
        if month < 1:
            month = 12
            current_year -= 1

        while current_date_valid(day, month, current_year) == False:
            day -= 1

    return day, month


def date_increase(day, month):
    global current_year
    day += 1
    if current_date_valid(day, month, current_year) != False:
        return day, month

    else:
        day = 1
        month += 1
        if month > 12:
            month = 1
            current_year += 1

        return day, month


def start_of_the_week(day, month):
    while date(current_year, month, day).weekday() != 0:
        day, month = date_decrease(day, month)

    return day, month


def create_week_list(day, month):
    global current_month, current_day
    week = []
    while len(week) < 7:
        if current_date_valid(day, month, current_year) == False:
            day, month = date_increase(day, month)
        current_date = date(current_year, month, day)
        current_month, current_day = month, day
        button = create_button(current_date)
        week.append(button)
        day += 1

    return week