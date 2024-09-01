# пока не работает
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from datetime import datetime

API_TOKEN = 'config.token_api'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Стейт машина для планирования события
class EventStates(StatesGroup):
    waiting_for_event_name = State()
    waiting_for_event_date = State()

# Словарь для хранения событий пользователей
user_events = {}

# Команда старт
@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я бот для планирования событий. Используй команду /newevent, чтобы создать событие.")

# Команда для создания нового события
@dp.message_handler(commands='newevent')
async def cmd_new_event(message: types.Message):
    await EventStates.waiting_for_event_name.set()
    await message.answer("Введите название события:")

# Получаем название события и запрашиваем дату
@dp.message_handler(state=EventStates.waiting_for_event_name)
async def process_event_name(message: types.Message, state: FSMContext):
    await state.update_data(event_name=message.text)
    await EventStates.next()
    await message.answer("Введите дату события в формате DD.MM.YYYY HH:MM:")

# Получаем дату события и сохраняем его
@dp.message_handler(state=EventStates.waiting_for_event_date)
async def process_event_date(message: types.Message, state: FSMContext):
    event_date = datetime.strptime(message.text, '%d.%m.%Y %H:%M')
    user_data = await state.get_data()

    event_name = user_data['event_name']
    user_id = message.from_user.id

    if user_id not in user_events:
        user_events[user_id] = []

    user_events[user_id].append((event_name, event_date))
    await message.answer(f"Событие '{event_name}' запланировано на {event_date.strftime('%d.%m.%Y %H:%M')}.")

    await state.finish()

# Команда для просмотра всех событий пользователя
@dp.message_handler(commands='myevents')
async def cmd_my_events(message: types.Message):
    user_id = message.from_user.id

    if user_id in user_events and user_events