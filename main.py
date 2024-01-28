# Импорты используемых библиотек
import asyncio  # Позволяет работать с асинхронными функциями
from aiogram import Bot, Dispatcher, types  # Базовые объекты для работы с ботами
from aiogram.filters import Command  # Фильтры для принятия входных сообщения
from aiogram.utils.keyboard import InlineKeyboardBuilder  # Импорт кнопок
import logging  # Получение информации о процессе работы бота
from auxiliary_modules import getPhrase, isUserInBase, isAdmin  # Моя библиотека для выбора рандомной фразы из базы
from custom_json import getData, addData, delData  # Моя библиотека для лёгкой работы с JSON-файлами
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import FSInputFile
from aiogram import F
import sys

logging.basicConfig(level=logging.INFO)  # Установка уровня логирования
dp = Dispatcher()  # Создание диспетчера
last_statuses = {}

configData = getData("data/config.json")  # Получение словаря со всеми параметрами бота
textsData = getData("data/texts.json")  # Получение словаря со всеми текстами бота
bot = Bot(token = configData["token"])  # Выдача телеграм-логина боту

@dp.message(Command("start"))  # Обработчик команды /start
async def startCMD(message: types.Message):
  user = message.from_user  # Получение информации о пользователе
  if not isUserInBase(user.id):  # Проверка на наличие пользователя в базе
    addData(
      'data/users.json',
      user.id,
      {
        "username": user.username, 
        "first name": user.first_name, 
        "last name": user.last_name
      }
    )  # Добавление пользователя в базу
  
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
    text=getPhrase(f"modes/{callback.data[:-5]}/description"),
    reply_markup=builder.as_markup()
  )

@dp.callback_query(lambda c: c.data.endswith(" function"))
async def functionFunctions(callback: types.CallbackQuery):
  function = callback.data[:-9]  # Callback-значение кнопки
  content = textsData["modes"][function]["topics"]

  # Создание кнопки возврата
  back_button = InlineKeyboardButton(
      text="Назад",
      callback_data="start"
  )
  
  # Создание списка кнопок
  keys = [
    [InlineKeyboardButton(
      text=content[topic]["name"],
      callback_data=topic + " topic"
    )] for topic in content
  ]

  # Добавление кнопки возврата
  keys.append([back_button])
  # Создание группы кнопок
  keyboard = InlineKeyboardMarkup(inline_keyboard=keys)

  await callback.message.edit_text(
    text=getPhrase(f"modes/{function}/choose topic"),
    reply_markup=keyboard
  )

@dp.callback_query(lambda c: c.data.endswith(" topic"))
async def topicFunctions(callback: types.CallbackQuery):
  topic = callback.data[:-6]  # Callback-значение кнопки
  content = textsData["modes"]["theory"]["topics"][topic]

  # Инициируем кнопку "Назад"
  back_button = InlineKeyboardButton(
    text="Назад",
    callback_data="theory function"
  )

  # Делаем список кнопок, чтобы они правильно выводились
  keys = [
    [InlineKeyboardButton(
      text=content["subtopics"][subtopic]["name"],
      callback_data=topic + "/" + subtopic + " subtopic"
    )] for subtopic in content["subtopics"]
  ]

  # Добавляем кнопку назад в группу
  keys.append([back_button])
  # Преобразуем список в группу кнопок
  keyboard = InlineKeyboardMarkup(inline_keyboard=keys)

  await callback.message.edit_text(
    text=getPhrase(f"modes/theory/topics/{topic}/description"),
    reply_markup=keyboard
  )

@dp.callback_query(lambda c: c.data.endswith(" subtopic"))
async def subtopicFunctions(callback: types.CallbackQuery):
  topic, subtopic = (callback.data[:-9]).split("/")  # Callback-значение кнопки
  content = textsData["modes"]["theory"]["topics"][topic]["subtopics"][subtopic]

  # Добавляем кнопку назад
  builder = InlineKeyboardBuilder()
  builder.button(text="Назад", callback_data=topic + " topic")

  # Отправляем описание подтемы с возможностью выбрать другую тему
  await callback.message.edit_text(
    text=content['description'],
    reply_markup=builder.as_markup()
  )

@dp.callback_query(lambda c: c.data == "help") # Обработчик кнопки "Помощь"
async def helpBTN(callback: types.CallbackQuery):
  builder = InlineKeyboardBuilder()
  builder.button(text="Начать", callback_data="start")

  # Выводим основную справку по боту
  await callback.message.edit_text(
    text=getPhrase('general help'),
    reply_markup=builder.as_markup()
  )

@dp.message(Command("users"))
async def sendUsersList(message: types.Message):
  # Проверяем находится ли пользователь в списке администраторов
  if isAdmin(message.from_user.id):
    # Отправляем документ со списком пользователей
    await message.answer_document(FSInputFile(path='data/users.json'))
  else:
    # Отвечаем отказом
    await message.answer(getPhrase("no permission"))

@dp.callback_query(lambda c: c.data)
async def emptyBTN(callback: types.CallbackQuery):
  # Выводим уведомление сверху при нажатии на пустую кнопку
  await callback.answer(getPhrase("empty button pressed"), show_alert=False)

@dp.message()  # В случае сообщений не попадающих под фильтры
async def textMessage(message: types.Message):
  # Отвечаем, что сообщение не предвидено
  await message.reply(getPhrase("unexpected message"))

async def main():
  await dp.start_polling(bot)  # Запуск сервера бота

if __name__ == "__main__":
  # sys.stdout = open('data/output.txt', 'w')
  asyncio.run(main())  # Запуск асинхронной функции main()
