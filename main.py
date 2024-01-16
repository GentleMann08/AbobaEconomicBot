# Импорты используемых библиотек
import asyncio  # Позволяет работать с асинхронными функциями
from aiogram import Bot, Dispatcher, types  # Базовые объекты для работы с ботами
from aiogram.filters import Command  # Фильтры для принятия входных сообщения
from aiogram.utils.keyboard import InlineKeyboardBuilder  # Импорт кнопок
import logging  # Получение информации о процессе работы бота
from auxiliary_modules import getPhrase  # Моя библиотека для выбора рандомной фразы из базы
from custom_json import getData, addData, delData  # Моя библиотека для лёгкой работы с JSON-файлами
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

logging.basicConfig(level=logging.INFO)  # Установка уровня логирования
dp = Dispatcher()  # Создание диспетчера
last_statuses = {}

configData = getData("data/config.json")  # Получение словаря со всеми параметрами бота
textsData = getData("data/texts.json")  # Получение словаря со всеми текстами бота
bot = Bot(token = configData["token"])  # Выдача телеграм-логина боту

@dp.message(Command("start"))  # Обработчик команды /start
async def startCMD(message: types.Message):
  # Делаем две кнопки
  builder = InlineKeyboardBuilder()  # Создаём клавиатуру типа InlineKeyboardBuilder
  builder.button(text="Начать", callback_data="start")
  builder.button(text="Помощь", callback_data="help")

  # Отвечаем пользователю на /start
  await message.answer(
    getPhrase("welcome"), 
    reply_markup=builder.as_markup()
  )

  # last_messages[message.chat.id] = bot_message  # Запись сообщения бота в словарь чатов
  last_statuses[message.chat.id] = "start"  # Выдаём статус общения бота с пользователем

@dp.callback_query(lambda c: c.data == "start") # Обработчик кнопки "Начать"
async def startBTN(callback: types.CallbackQuery):
  # Добавляем клавиатуру, которая будет выводить кнопки в разные строки
  keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(
        text=textsData["modes"][mode]["name"],
        callback_data=(mode + " mode"))] for mode in configData["modes"]])

  #  Спрашиваем у пользователя, какой режим он хочет выбрать
  await callback.message.edit_text(
    text=getPhrase('choose mode'),
    reply_markup=keyboard
  )

# Если пользователь выбрал режим, то в callback в конце будет стоять " mode"
@dp.callback_query(lambda c: c.data.endswith(" mode"))
async def modeFunctions(callback: types.CallbackQuery):
  builder = InlineKeyboardBuilder()
  action_mode = f'{callback.data[:-5]} function'  # Callback-значение кнопки
  button_text = getPhrase('start')  # Кнопка для утверждения выбора функции

  builder.button(text=button_text, callback_data=action_mode)  # Ведём к полноценной функции
  builder.button(text=getPhrase("back"), callback_data="start")  # Кнопка "Назад"

  await callback.message.edit_text(
    text=getPhrase(f"modes/{callback.data[:-5]}/discription"),
    reply_markup=builder.as_markup()
  )

@dp.callback_query(lambda c: c.data.endswith(" function"))
async def economicFacts(callback: types.CallbackQuery):
  keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(
        text=f"{grade}-й класс",
        callback_data=f"{callback.data[:-9]} {grade} grade")] for grade in [9, 10, 11]])
  
  keyboard.inline_keyboard.append([InlineKeyboardButton(
        text=getPhrase("back"),
        callback_data="start")])
  
  await callback.message.edit_text(
    text=getPhrase("modes/choose grade"),
    reply_markup=keyboard
  )

@dp.callback_query(lambda c: c.data == "empty button")
async def emptyBTN(callback: types.CallbackQuery):
  # Выводим уведомление сверху при нажатии на пустую кнопку
  await callback.answer(getPhrase("empty button pressed"), show_alert=False)

@dp.callback_query(lambda c: c.data == "help") # Обработчик кнопки "Помощь"
async def helpBTN(callback: types.CallbackQuery):
  builder = InlineKeyboardBuilder()
  builder.button(text="Начать", callback_data="start")

  await callback.message.edit_text(
    text=getPhrase('general help'),
    reply_markup=builder.as_markup()
  )

@dp.message()  # В случае сообщений не попадающих под фильтры
async def textMessage(message: types.Message):
  await message.reply(getPhrase("unexpected message"))

async def main():
  await dp.start_polling(bot)  # Запуск сервера бота

if __name__ == "__main__":
  asyncio.run(main())  # Запуск асинхронной функции main()
