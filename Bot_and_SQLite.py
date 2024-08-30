import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
import sqlite3
from datetime import datetime

API_TOKEN = 'YOUR_BOT_TOKEN'
ADMIN_ID = 123456789  # Замените на ID администратора

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class AppointmentStates(StatesGroup):
    waiting_for_teacher = State()
    waiting_for_datetime = State()

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS appointments
                 (id INTEGER PRIMARY KEY,
                  user_id INTEGER,
                  teacher TEXT,
                  date_time TEXT,
                  created_at TEXT)''')
    conn.commit()
    conn.close()

# Добавление записи
def add_appointment(user_id, teacher, date_time):
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO appointments (user_id, teacher, date_time, created_at) VALUES (?, ?, ?, ?)",
              (user_id, teacher, date_time, created_at))
    conn.commit()
    conn.close()

# Получение записей пользователя
def get_user_appointments(user_id):
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    c.execute("SELECT teacher, date_time FROM appointments WHERE user_id = ?", (user_id,))
    appointments = c.fetchall()
    conn.close()
    return appointments

# Получение всех записей (для админа)
def get_all_appointments():
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    c.execute("SELECT user_id, teacher, date_time FROM appointments")
    appointments = c.fetchall()
    conn.close()
    return appointments

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Записаться", "Мои записи", "Выход"]
    keyboard.add(*buttons)
    await message.reply("Выберите действие:", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "Записаться")
async def start_appointment(message: types.Message):
    await AppointmentStates.waiting_for_teacher.set()
    await message.reply("Введите имя преподавателя:")

@dp.message_handler(state=AppointmentStates.waiting_for_teacher)
async def process_teacher(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['teacher'] = message.text
    await AppointmentStates.waiting_for_datetime.set()
    await message.reply("Введите дату и время встречи (формат: ГГГГ-ММ-ДД ЧЧ:ММ):")

@dp.message_handler(state=AppointmentStates.waiting_for_datetime)
async def process_datetime(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['date_time'] = message.text
    
    add_appointment(message.from_user.id, data['teacher'], data['date_time'])
    await message.reply("Запись добавлена.")
    await state.finish()

@dp.message_handler(lambda message: message.text == "Мои записи")
async def show_appointments(message: types.Message):
    appointments = get_user_appointments(message.from_user.id)
    if appointments:
        response = "Ваши записи:\n"
        for teacher, date_time in appointments:
            response += f"Преподаватель: {teacher}, Время: {date_time}\n"
    else:
        response = "У вас нет записей."
    await message.reply(response)

@dp.message_handler(lambda message: message.text == "Выход")
async def exit_bot(message: types.Message):
    await message.reply("До свидания!")

@dp.message_handler(commands=['admin'])
async def admin_command(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        appointments = get_all_appointments()
        if appointments:
            response = "Все записи:\n"
            for user_id, teacher, date_time in appointments:
                response += f"Пользователь: {user_id}, Преподаватель: {teacher}, Время: {date_time}\n"
        else:
            response = "Записей нет."
        await message.reply(response)
    else:
        await message.reply("У вас нет доступа к этой команде.")

if __name__ == '__main__':
    init_db()
    executor.start_polling(dp, skip_updates=True)
