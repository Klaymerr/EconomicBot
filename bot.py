import asyncio
import os.path

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import Message, CallbackQuery
from jedi.api.refactoring import inline

bot_token = '7648099339:AAHH5sn7k7pRSYt6ua6dKYwu9hhNnZ1v5LU'
user_path = 'users'
news_path = 'news'

dp = Dispatcher()
bot = Bot(token=bot_token)

class UserInfo(StatesGroup):
    name = State()
    age = State()

@dp.message(CommandStart())
async def start(message: Message):
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Профиль')],
                                       [KeyboardButton(text='НеАктуальные котировки')],
                                       [KeyboardButton(text='Новости Пензы')]],
                             resize_keyboard=True,
                             input_field_placeholder='И че делать будем то?',
                             )
    await message.answer('hi', reply_markup=kb)

@dp.message(F.text == 'Профиль')
async def Reg(message:Message, state : FSMContext):
    id = str(message.from_user.id)

    if os.path.exists(user_path + '/' + id + '.txt'):
        data = open(user_path + '/' + id+'.txt')
        for i in data:
            info = [x for x in i.split()]
        await message.answer(f'Имя: {info[0]}\nВозраст: {info[1]}')
    else:
        await state.set_state(UserInfo.name)
        await message.answer('Введите имя:')

@dp.message(UserInfo.name)
async def name(message : Message, state : FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(UserInfo.age)
    await message.answer('Введите возраст')

@dp.message(UserInfo.age)
async def age(message : Message, state : FSMContext):
    await state.update_data(age=message.text)
    data = await state.get_data()
    await message.answer(f'Сногсшибательно\nИмя: {data["name"]}\nВозраст: {data["age"]}')

    id = str(message.from_user.id)
    f = open(user_path + '/' + id + '.txt', 'w')
    f.write(data["name"] + ' ' + data["age"])
    f.close()

    await state.clear()

@dp.message(F.text == 'Новости Пензы')
async def News(message: Message):
    for name in os.listdir(news_path):
        f = open(news_path + '/' + name, encoding = 'utf-8')
        await message.answer(f.read())

@dp.message(F.text == 'НеАктуальные котировки')
async def Cot(message: Message):
    f = open('quotes.txt')
    nw = []
    for line in f:
        nw.append([x for x in line.split()])

    text = ''
    for x in nw:
        text += x[0] + ' ' + str(x[1]) + '$\n'
    await message.answer(text)


async def main() -> None:
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
