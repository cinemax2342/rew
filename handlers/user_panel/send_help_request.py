from aiogram import F, types, Router, Bot
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from filter.chat_types import ChatTypeFilter
from handlers.user_panel.start_functions import user_preferences
from keyboard.inline import language_selection_keyboard, start_functions_keyboard, return_inline_keyboard
from keyboard.reply import get_cancel_keyboard as get_return_keyboard
from message_text.text import messages, cancel

send_help_request_private_router = Router()
send_help_request_private_router.message.filter(ChatTypeFilter(['private']))
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отмена")],
    ],
    resize_keyboard=True,
)


class SendHelpRequestState(StatesGroup):
    username = State()
    fullname = State()
    group = State()
    problem = State()
    media = State()


@send_help_request_private_router.message(Command('send_help_request'))
async def send_help_request_private(message: Message, state: FSMContext):
    user_id = message.from_user.id
    language = user_preferences.get(user_id, {}).get('language', 'ru')
    await state.set_state(SendHelpRequestState.fullname)
    await message.answer(messages[language]['enter_fullname'], reply_markup=get_return_keyboard(language))


@send_help_request_private_router.callback_query(F.data.startswith('send_help_request'))
async def send_help_request_private(query: types.CallbackQuery, state: FSMContext):
    message = query.message
    user_id = message.from_user.id
    language = user_preferences.get(user_id, {}).get('language', 'ru')
    await state.set_state(SendHelpRequestState.fullname)
    await message.answer(messages[language]['enter_fullname'], reply_markup=get_return_keyboard(language))


@send_help_request_private_router.message(SendHelpRequestState.fullname)
async def process_fullname(message: Message, state: FSMContext):
    username = message.from_user.username if message.from_user.username else message.from_user.first_name
    await state.update_data(username=username)
    user_id = message.from_user.id
    language = user_preferences.get(user_id, {}).get('language', 'ru')
    if message.text in cancel:
        await state.clear()
        await message.answer(messages[language]['request_canceled'], reply_markup=return_inline_keyboard(language))
    elif message.text:
        await state.update_data(fullname=message.text)
        await state.set_state(SendHelpRequestState.group)
        await message.answer(messages[language]['enter_group'], reply_markup=get_return_keyboard(language))
    else:
        await message.delete()
        await message.answer(messages[language]['enter_fullname'], reply_markup=get_return_keyboard(language))


@send_help_request_private_router.message(SendHelpRequestState.group)
async def process_group(message: Message, state: FSMContext):
    user_id = message.from_user.id
    language = user_preferences.get(user_id, {}).get('language', 'ru')

    if message.text in cancel:
        await state.clear()
        await message.answer(messages[language]['request_canceled'], reply_markup=return_inline_keyboard(language))
    elif message.text:
        await state.update_data(group=message.text)
        await state.set_state(SendHelpRequestState.problem)
        await message.answer(messages[language]['describe_problem'], reply_markup=get_return_keyboard(language))
    else:
        await message.delete()
        await message.answer(messages[language]['enter_group'], reply_markup=get_return_keyboard(language))


@send_help_request_private_router.message(SendHelpRequestState.problem)
async def process_problem(message: Message, state: FSMContext):
    user_id = message.from_user.id
    language = user_preferences.get(user_id, {}).get('language', 'ru')

    if message.text in cancel:
        await state.clear()
        await message.answer(messages[language]['request_canceled'], reply_markup=return_inline_keyboard(language))
        return

    # Обновляем данные состояния
    await state.update_data(problem=message.text if message.text else "")

    # Переход к состоянию для загрузки медиафайлов
    await state.set_state(SendHelpRequestState.media)
    await message.answer(messages[language]['describe_problem_media'], reply_markup=get_return_keyboard(language))


@send_help_request_private_router.message(SendHelpRequestState.media)
async def process_media(message: Message, state: FSMContext, bot: Bot):
    group_id = bot.group_id
    user_id = message.from_user.id
    language = user_preferences.get(user_id, {}).get('language', 'ru')
    data = await state.get_data()
    username = data['username']
    fullname = data['fullname']
    group = data['group']
    problem = data['problem']

    if message.text in cancel:
        await state.clear()
        await message.answer(messages[language]['request_canceled'], reply_markup=return_inline_keyboard(language))
        return

    additional_info = (
        f"🆕 Новое сообщение\n"
        f"Пользователь: @{username}\n"
        f"Полное имя: {fullname}\n"
        f"Группа: {group}\n"
        f"Проблема: {problem}\n"
    )

    if message.photo:
        file_id = message.photo[-1].file_id
        await bot.send_photo(
            chat_id=group_id,
            photo=file_id,
            caption=f"{additional_info}"
        )

    elif message.video:
        file_id = message.video.file_id
        await bot.send_video(
            chat_id=group_id,
            video=file_id,
            caption=f"{additional_info}"
        )

    elif message.voice:
        file_id = message.voice.file_id
        await bot.send_voice(
            chat_id=group_id,
            voice=file_id,
            caption=f"{additional_info}"
        )

    elif message.document:
        file_id = message.document.file_id
        await bot.send_document(
            chat_id=group_id,
            document=file_id,
            caption=f"{additional_info}"
        )

    elif message.text:
        await bot.send_message(
            chat_id=group_id,
            text=f"{additional_info}\n"
        )

    # Подтверждение отправки пользователю после отправки сообщения в группу
    await message.answer(messages[language]['request_sent'], reply_markup=return_inline_keyboard(language))
    await state.clear()

