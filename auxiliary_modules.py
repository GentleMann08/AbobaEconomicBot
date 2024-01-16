from custom_json import addData, delData, getData
import openai
from random import choice
import json
from aiogram import types


# Функция для выдали фразы из базы с текстами
def getPhrase(key):
  texts_data = getData('data/texts.json')
  if "/" in key:
    phrase = texts_data
    keys = list(key.split("/"))
    for key in keys:
      phrase = phrase[key]
  else:
    phrase = texts_data[key]
  if type(phrase) == list:
    return choice(phrase)
  return phrase



def findUserById(user_id):
  with open('data/users.json', 'r', encoding='utf-8') as json_file:
    user_list = json.load(json_file)
  for user in user_list:
    if user['user_id'] == user_id:
      return user
  return None


def isAdmin(user_id):
  config = getData('data/config.json')
  admins = config['admins']  
  if user_id in admins:
    return True
  else:
    return False


def generateResponse(prompt):
  settings = getData("data/gpt_config.json")
  openai.api_key = settings["openai key"]
  completions = openai.Completion.create(engine=settings["engine"],
                                         prompt=prompt,
                                         max_tokens=settings["max_tokens"],
                                         n=settings["n"],
                                         stop=None,
                                         temperature=settings["temperature"])

  message = completions.choices[0].text.strip()
  return message