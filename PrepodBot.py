import logging
import asyncio
import json
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import config

API_TOKEN = config.token_api

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Файл для хранения уроков
LESSONS_FILE = 'lessons.json'

# Функция для загрузки уроков из файла
def load_lessons():
    try:
        with open(LESSONS_FILE, 'r') as file:
            data = json.load(file)
            logging.info(f"Загруженные уроки: {data}")
            return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Ошибка загрузки уроков: {e}")
        return {}

# Функция для сохранения уроков в файл
def save_lessons(lessons):
    with open(LESSONS_FILE, 'w') as file:
        json.dump(lessons, file)

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет 😋! Используй /schedule для планирования урока.")

# Хэндлер на команду /schedule
@dp.message(Command("schedule"))
async def cmd_schedule(message: types.Message):
    await message.answer("Введите дату и время урока в формате 'YYYY-MM-DD HH:MM'.")

# Хэндлер для обработки даты и времени
@dp.message()
async def process_schedule(message: types.Message):
    # Проверяем, что это не команда
    if message.text.startswith('/'):
        return  # Игнорируем команды

    try:
        # Пробуем преобразовать текст в дату и время
        lesson_time = datetime.strptime(message.text, '%Y-%m-%d %H:%M')

        # Проверяем, что урок не запланирован в прошлом
        if lesson_time < datetime.now():
            await message.answer("Нельзя запланировать урок в прошлом. Пожалуйста, выберите будущее время.")
            return

        # Загружаем существующие уроки
        lessons = load_lessons()
        user_id = str(message.from_user.id)  # Преобразуем ID пользователя в строку для хранения в JSON

        # Сохраняем урок
        if user_id not in lessons:
            lessons[user_id] = []

        lessons[user_id].append(lesson_time.strftime('%Y-%m-%d %H:%M'))  # Сохраняем в строковом формате

        # Сохраняем обновленный словарь в файл
        save_lessons(lessons)

        logging.info(f"Урок запланирован: {lesson_time} для пользователя ID: {user_id}")
        await message.answer(f"Урок запланирован на {lesson_time.strftime('%Y-%m-%d %H:%M')}!")
    except ValueError:
        await message.answer("Неверный формат! Пожалуйста, используйте 'YYYY-MM-DD HH:MM'.")

# Хэндлер на команду /lessons для отображения запланированных уроков
@dp.message(Command("lessons"))
async def cmd_lessons(message: types.Message):
    user_id = str(message.from_user.id)  # Преобразуем ID пользователя в строку
    lessons = load_lessons()

    user_lessons = lessons.get(user_id, [])

    logging.info(f"Загруженные уроки: {user_lessons}")

    if not user_lessons:
        await message.answer("У вас нет запланированных уроков.")
        return

    response = "Запланированные уроки:\n"
    for lesson_time in sorted(user_lessons, key=lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M')):
        response += f"- {lesson_time}\n"

    await message.answer(response)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())