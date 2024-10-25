from aiogram import F, Router, types, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from filter.chat_types import ChatTypeFilter, IsAdmin
from handlers.user_panel.start_functions import user_preferences
from keyboard.inline import return_inline_keyboard
from keyboard.reply import get_cancel_keyboard
from message_text.text import messages, cancel

# Router for handling review messages
review_private_router = Router()
review_private_router.message.filter(ChatTypeFilter(['private']))


class ReviewState(StatesGroup):
    WaitingForReview = State()


@review_private_router.message(Command("leave_review"))
async def send_review_request(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    language = user_preferences.get(user_id, {}).get('language', 'ru')  # Получаем язык пользователя
    await message.answer(
        text=messages[language]['review'],
        reply_markup=get_cancel_keyboard(language)  # Отправляем сообщение с текстом отзыва
    )
    await state.set_state(ReviewState.WaitingForReview)  # Устанавливаем состояние ожидания отзыва


@review_private_router.callback_query(F.data.startswith("leave_review"))
async def send_review_request_callback_query(query: types.CallbackQuery, state: FSMContext) -> None:
    await query.message.delete()
    user_id = query.from_user.id
    language = user_preferences.get(user_id, {}).get('language', 'ru')  # Получаем язык пользователя
    await query.message.answer(
        text=messages[language]['review'],
        reply_markup=get_cancel_keyboard(language)  # Отправляем сообщение с текстом отзыва
    )
    await state.set_state(ReviewState.WaitingForReview)


@review_private_router.message(ReviewState.WaitingForReview)
async def process_review(message: types.Message, state: FSMContext, bot: Bot):
    keyboard = ReplyKeyboardRemove()
    language = user_preferences.get(message.from_user.id, {}).get('language', 'ru')
    group_id = bot.group_id

    if message.text in cancel:
        await state.clear()
        await message.answer(messages[language]['request_canceled'], reply_markup=return_inline_keyboard(language))
        return

    elif message.text:
        user_info = f"{message.from_user.first_name}"
        if message.from_user.last_name:
            user_info += f" {message.from_user.last_name}"
        if message.from_user.username:
            user_info += f" (@{message.from_user.username})"
        review_text = message.text
        review_message = f"💬 Отзыв от {user_info}:\n\n{review_text}"
        await bot.send_message(chat_id=group_id, text=review_message)
        await message.answer(text=messages[language]['review_thanks'], reply_markup=keyboard)
        await state.clear()
    else:
        await message.answer(text=messages[language]['review_invalid'], reply_markup=keyboard)
