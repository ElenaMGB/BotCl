# пока не работает
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from datetime import datetime
import logging

API_TOKEN = 'YOUR_BOT_API_TOKEN'

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Словарь для хранения событий по пользователям
user_events = {}

# Определение состояний для FSM
class EventForm(StatesGroup):
    title = State()
    date = State()

# Команда /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я бот для планирования событий. Используй /newevent для создания нового события и /viewevents для просмотра запланированных событий.")

# Команда /newevent для создания нового события
@dp.message_handler(commands=['newevent'])
async def new_event(message: types.Message):
    await message.reply("Введите название события:")
    await EventForm.title.set()

# Получение названия события
@dp.message_handler(state=EventForm.title)
async def process_title(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['title'] = message.text
    await EventForm.next()
    await message.reply("Введите дату и время события в формате ДД.ММ.ГГГГ ЧЧ:ММ:")

# Получение даты и времени события
@dp.message_handler(state=EventForm.date)
async def process_date(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        try:
            event_date = datetime.strptime(message.text, '%d.%m.%Y %H:%M')
            user_id = message.from_user.id
            if user_id not in user_events:
                user_events[user_id] = []
            user_events[user_id].append({'title': data['title'], 'date': event_date})
            await message.reply(f"Событие '{data['title']}' запланировано на {event_date.strftime('%d.%m.%Y %H:%M')}")
        except ValueError:
            await message.reply("Неверный формат даты. Попробуйте снова:")
            return

    await state.finish()

# Команда /viewevents для просмотра запланированных событий
@dp.message_handler(commands=['viewevents'])
async def view_events(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_events and user_events[user_id]:
        events_text = "Ваши запланированные события:\n\n"
        for idx, event in enumerate(user_events[user_id], 1):
            events_text += f"{idx}. {event['title']} - {event['date'].strftime('%d.%m.%Y %H:%M')}\n"
        await message.reply(events_text)
    else:
        await message.reply("У вас нет запланированных событий.")

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
