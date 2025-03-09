import asyncio
import os.path
import requests
import json
import time
import random

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import Message, CallbackQuery

from secrets import user_path, fin_token, ny_token

router = Router()

class UserInfo(StatesGroup):
    name = State()
    age = State()

@router.message(CommandStart())
async def start(message: Message):
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Профиль')],
                                       [KeyboardButton(text='Котировки')],
                                       [KeyboardButton(text='Новости Пензы')]],
                             resize_keyboard=True,
                             input_field_placeholder='И че делать будем то?',
                             )
    await message.answer('Добро пожаловать!', reply_markup=kb)

@router.message(F.text == 'Профиль')
async def Reg(message:Message, state : FSMContext):
    id = str(message.from_user.id)

    if os.path.exists(user_path + '/' + id + '.json'):
        data = json.load(open(user_path + '/' + id+'.json'))

        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Изменить', callback_data='change')]])
        await message.answer(f'Имя: {data["name"]}\nВозраст: {data["age"]}', reply_markup=kb)
    else:
        await state.set_state(UserInfo.name)
        await message.answer('Введите имя:')

@router.callback_query(lambda c : c.data == 'change')
async def ch(callback: CallbackQuery, state : FSMContext):
    try:
        os.remove(user_path + '/' + str(callback.from_user.id) + '.json')
    except FileNotFoundError:
        None
    await callback.answer('Как скажешь')
    await state.set_state(UserInfo.name)
    await callback.message.answer('Введите имя:')


@router.message(UserInfo.name)
async def name(message : Message, state : FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(UserInfo.age)
    await message.answer('Введите возраст')

@router.message(UserInfo.age)
async def age(message : Message, state : FSMContext):
    await state.update_data(age=message.text)
    data = await state.get_data()
    await message.answer(f'Сногсшибательно\nИмя: {data["name"]}\nВозраст: {data["age"]}')

    id = str(message.from_user.id)
    f = open(user_path + '/' + id + '.json', 'w')
    json.dump(data, f, ensure_ascii=False, indent=4)
    f.close()

    await state.clear()


news = ''
news_time = 0

@router.message(F.text == 'Новости Пензы')
async def News(message: Message):
    global news
    global news_time
    if(time.time() - news_time < 300):
        await message.answer(text = news, parse_mode = ParseMode.HTML)
    else:
        resp = requests.get(f'https://api.nytimes.com/svc/news/v3/content/all/business.json?limit=3&offset=0&api-key={ny_token}')
        if(resp.status_code == 200):
            news = ''
            for i in range(3):
                title = str(resp.json()["results"][i]["title"])
                text = str(resp.json()["results"][i]["abstract"])
                url = str(resp.json()["results"][i]['url'])
                if(news != ''):
                    news += '\n\n'
                news += f"<a href='{url}'>{title}</a>" + f'\n\t{text}'
            news_time = time.time()
            await message.answer(text = news, parse_mode = ParseMode.HTML)
        else:
            await message.answer('Мир прогнил никаких тебе новостей')

@router.message(F.text == 'Котировки')
async def Cot(message: Message):
    mes = await message.answer('ЩАЩАЩА СЧИТАЮ ПОДОЖДИ ЩА БУДЕТ ВСЁ...')
    f = open('quotes.txt')
    t = ''
    for line in f:
        resp = requests.get(f"https://finnhub.io/api/v1/quote?symbol={line.strip()}&token={fin_token}")
        if(resp.status_code == 200):
            t += line.strip() + '\t' + str(resp.json()["c"]) + '\n'
        else:
            t = 'AAAAAAAAAA ИДИ НАХУЙ'
            break

    await mes.delete()
    await message.answer(t)
