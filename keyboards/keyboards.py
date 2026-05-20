from aiogram.types import KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def btn_yes_no():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text='/help'))
    builder.add(KeyboardButton(text='/cancel'))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def btn_add_workout_goal(btn_yes_for_goal,  btn_no):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text='Да, для цели', callback_data=btn_yes_for_goal))
    builder.add(InlineKeyboardButton(text='Нет', callback_data=btn_no))
    return builder.as_markup()


def btn_select_number_goal(numbers: str):
    builder = InlineKeyboardBuilder()
    for number in numbers.split(','):
        builder.add(InlineKeyboardButton(text=f'Цель № {number}', callback_data=number))
    builder.adjust(3)
    return builder.as_markup()
