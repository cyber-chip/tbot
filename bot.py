from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import Message, CallbackQuery
from settings import TOKEN
from datetime import datetime, date, time
import logging
import datetime
import sqlite3
import os
bot = Bot(token=TOKEN)

dp = Dispatcher(bot)
connection = sqlite3.connect('database.db')
cur = connection.cursor()
#db = ('database.db')
cur.execute("""CREATE TABLE IF NOT EXISTS users (id, username, start_date, points, passed_the_test, reg)""")

file_bd = "database.db"
if os.access(file_bd, os.F_OK) == True:
            print("Файл базы данных создан")

else:
    print('Ошибка зоздания файла базы данных')


#Будем записывать отчет о работе бота
logging.basicConfig(filename='bot.log', level=logging.DEBUG)

#index_button = 'Главная' 
student_registration = 'Регистрация'
start_the_test = 'Начать тест'
stats = 'Статистика'
#support = 'Задать вопрос'

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(student_registration, start_the_test, stats)
    #markup.row(support)
    # - Получаем id и username человека
    id = message.chat.id
    print(id)

    username = message.chat.username
    print(username)

    # - Делаем проверку на то, есть ли пользователь в базе
    cur.execute(f"SELECT id from users WHERE id={id}")
    user = cur.fetchall()
    is_user = len(user)
    print('2')
    print(is_user,id)

    #дата время регистрации
    now = datetime.datetime.now()
    is_datatime = str(now)
    #Если пользователя нет, заносим его в базу данных
    print('3')
   
    if is_user <= 0: #если reg заполнен то регистрация нового usera не происходит
        print(username)      
        #данные для таблицы базы данных     
        table_users = [((id), (username), (is_datatime), 0, 0, 0)]
        #как пользователь подключается к боту его данные сохранются в базу данных
        cur.executemany("INSERT INTO users VALUES (?, ?, ?, ?, ?,?);", table_users)
        connection.commit()
        
        text_answer = f'Добро пожаловать {username}! Вы успешно зарегестрированы.'
        await message.answer(text=text_answer, reply_markup=markup)
        connection.commit()
           
    else:  
        text_answer = f'{username} Зарегистрируйтесь чтобы начать тестирование'
        await message.answer(text=text_answer, reply_markup=markup)

#####################################################################
@dp.message_handler(text=student_registration)
async def process_stats(message: Message):


    id = message.chat.id
    username = message.chat.username

    cur.execute(f"SELECT reg from users WHERE id={id}")
    reg = cur.fetchall()[0]
    is_reg = reg[0]
    print('reg')
    print(is_reg,id)
    
    if is_reg == 0:
        await message.answer(f'{username} Нужно зарегистрироватся, введите Ф.И.О!')
        print('Ф.И.О', id)      
        @dp.message_handler()
        async def process_stats(message: Message):
            id = message.chat.id #баз этой строчки будет траблы при регистрации !
            fio = message.text
            cur.execute('UPDATE users SET reg = ? WHERE id = ?', (fio, id))            
            print(fio, id)
            connection.commit()
            await message.answer(f'{fio} вы успешно зарегистрировались.')                             
    else: 
        await message.answer('Вы уже зарегистрировались, начните тестирование!')

#####################################################################           
@dp.message_handler(text=stats)
async def process_stats(message: Message):

    id = message.chat.id
    cur.execute(f"SELECT passed_the_test from users WHERE id={id}")
    passed_the_test = cur.fetchall()[0]
    is_passed_the_test = passed_the_test[0]
    print(is_passed_the_test, id)  # тут остановился!
    print('1')
    if is_passed_the_test >= 1:
        print('2')
        id = message.chat.id
        cur.execute(f"SELECT passed_the_test from users WHERE id={id}")
        passed_the_test = cur.fetchall()[0]
        is_passed_the_test = passed_the_test[0]
        #points = processed_data(db.fetchall(f"SELECT passed_the_test from users WHERE id={id}"))
        await message.answer(f' Ваши баллы: {is_passed_the_test}')
    else: 
        await message.answer('После пройденного теста Вам будет доступна статистика балов')

#модуль тестов
#при нажатии на кнопку начать тест.
@dp.message_handler(text=start_the_test)
async def start_cmd_handler(message: types.Message): 

    keyboard_markup = types.InlineKeyboardMarkup(row_width=3)

    text_and_data = (
        ('A', 'a'),
        ('B', 'b'),
        ('C', 'c'),
        ('D', 'd'),
    )
    row_btns = (types.InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)

    keyboard_markup.row(*row_btns)
    
    with open('images/t1.png', 'rb') as photo:

    
     await bot.send_photo(chat_id=message.chat.id, photo=photo, reply_markup=keyboard_markup,)

    
@dp.callback_query_handler(text='a')  
@dp.callback_query_handler(text='b') 
@dp.callback_query_handler(text='c')  
@dp.callback_query_handler(text='d')
async def inline_kb_answer_callback_handler(query: types.CallbackQuery):
    
    answer_data = query.data
    await query.answer(f'Вы ответили {answer_data!r}')
    if answer_data == 'a':

        #id = message.chat.id ##это зависает  
        #cur.execute(f"SELECT passed_the_test FROM users WHERE id={id}") 
        
        cur.execute("SELECT passed_the_test FROM users;")
        one_result = cur.fetchone()
        bal1 = 1 + sum(one_result)
        print(bal1)
        cur.execute('UPDATE users SET passed_the_test = ?', (bal1,))
        text = 'Ответ A принят!' 
        connection.commit()
    elif answer_data == 'b':
        text = 'Ответ B принят!'
    elif answer_data == 'c':
        text = 'Ответ C принят!'
    elif answer_data == 'd':
        text = 'Ответ D принят!'        
    else:
        text = f'Unexpected callback data {answer_data!r}!'

    await bot.send_message(query.from_user.id, text)
    
 
if __name__ == '__main__':
    
    executor.start_polling(dp, skip_updates=True)    
