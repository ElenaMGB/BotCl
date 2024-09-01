from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
import config

API_TOKEN = config.token_api
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Записать", "Прочитать", "Выход"]
    keyboard.add(*buttons)
    await message.reply("Выберите действие:", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "Записать")
async def write_message(message: types.Message):
    await message.reply("Введите сообщение для записи:")
    dp.register_message_handler(save_message, state="*", content_types=types.ContentTypes.TEXT)

async def save_message(message: types.Message):
    with open('messages.txt', 'a') as file:
        file.write(f"{message.text}\n")
    await message.reply("Сообщение записано.")
    dp.message_handlers.unregister(save_message)

@dp.message_handler(lambda message: message.text == "Прочитать")
async def read_messages(message: types.Message):
    try:
        with open('messages.txt', 'r') as file:
            content = file.read()
        await message.reply(content if content else "Сообщений нет.")
    except FileNotFoundError:
        await message.reply("Файл с сообщениями не найден.")

@dp.message_handler(lambda message: message.text == "Выход")
async def exit_bot(message: types.Message):
    await message.reply("До свидания!")
    await bot.close()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
