from aiogram.types import InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder

from message_text.text import messages


def start_functions_keyboard(language: str):
    """Функция для создания клавиатуры выбора языка."""
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=messages[language]['send_help_request'], callback_data='send_help_request'))
    keyboard.add(InlineKeyboardButton(text=messages[language]['leave_review'], callback_data='leave_review'))
    keyboard.add(InlineKeyboardButton(text=messages[language]['materials'], callback_data='materials')),
    keyboard.add(InlineKeyboardButton(text=messages[language]['help'], callback_data='help')),
    keyboard.add(InlineKeyboardButton(text=messages[language]['select_language'], callback_data='select_language'))



    return keyboard.adjust(2).as_markup()


def language_selection_keyboard(language: str):
    """Функция для создания клавиатуры выбора языка."""
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_language_ru"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="set_language_en"),
        InlineKeyboardButton(text="🇰🇬 Кыргызча", callback_data="set_language_kgz"),
        InlineKeyboardButton(text=messages[language]['return'], callback_data="start"),
    )
    return keyboard.adjust(3).as_markup()


def return_inline_keyboard(language: str):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text=messages[language]['return'], callback_data="start"),
    )
    return keyboard.adjust().as_markup()


def materials_inline_keyboard(language: str):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text='HTML,CSS', url='https://developer.mozilla.org/ru/docs/Learn'
                                                                      '/Getting_started_with_the_web/What_will_your_website_look_like'),
        InlineKeyboardButton(text='JS', url='https://developer.mozilla.org/ru/docs/Learn'),
        InlineKeyboardButton(text='PYTHON', url="https://www.w3schools.com/python/"),
        InlineKeyboardButton(text='GIT', url='https://git-scm.com/'),
        InlineKeyboardButton(text=messages[language]['return'], callback_data="start"),

    )
    return keyboard.adjust(2).as_markup()