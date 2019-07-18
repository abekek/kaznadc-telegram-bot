import telegram
import datetime
import time
import sqlite3
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters, ConversationHandler, RegexHandler
from functools import wraps
from telegram import ChatAction, InlineKeyboardButton, ForceReply, KeyboardButton, Contact
import logging
import os
import psycopg2
#from firebase import firebase
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import json
import emoji
import datetime
import flag
from config import token, certificate, db_url

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

TYPE, ATHLETE, GUEST, FIRST, REGISTER, SEND, LOCATION, QUESTION, FOOD, EXCRETE = range(10)

cred = credentials.Certificate(certificate)

firebase_admin.initialize_app(cred, {
    'databaseURL': db_url
})
ref = db.reference('users')

user_id_global = ""
type_of_user_int = 0

def start(bot, update):
    bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.ChatAction.TYPING)
    time.sleep(1)
    custom_keyboard = [['Спортсмен/Спортшы'], ['Гость/Қонақ']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat_id, text=flag.flagize(':RU:') +' Кто вы?' + '\n\n' + flag.flagize(':KZ:') + ' Сіз кімсіз?', reply_markup=reply_markup)
    reply_markup = telegram.ReplyKeyboardRemove()
    return TYPE

def type_of_user(bot, update):
    if(update.message.text == 'Гость/Қонақ'):
        guest_login(bot, update)
        return GUEST
    if(update.message.text == 'Спортсмен/Спортшы'):
        athlete_auth(bot, update)
        return FIRST

def athlete_login(bot, update):
    bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.ChatAction.TYPING)
    time.sleep(1)
    custom_keyboard = [['Список документов/Құжаттар тізімі', 'FAQ'], ['Отправить данные/Деректерді жіберу'], ['Задать вопрос/Сұрақ қою'], ['Назад/Артқа']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat_id, text=flag.flagize(':RU:') + ' Что вы хотите сделать?' + '\n\n' + flag.flagize(':KZ:') + ' Сіз не істегіңіз келеді?', reply_markup=reply_markup)
    reply_markup = telegram.ReplyKeyboardRemove()

def guest_login(bot, update):
    bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.ChatAction.TYPING)
    time.sleep(1)
    custom_keyboard = [['Список документов/Құжаттар тізімі', 'FAQ'], ['Задать вопрос/Сұрақ қою'], ['Назад/Артқа']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat_id, text=flag.flagize(':RU:') + ' Что вы хотите сделать?' + '\n\n' + flag.flagize(':KZ:') + ' Сіз не істегіңіз келеді?', reply_markup=reply_markup)
    reply_markup = telegram.ReplyKeyboardRemove()

def guest_choice(bot, update):
    global type_of_user_int
    type_of_user_int = 0
    if(update.message.text == 'Список документов/Құжаттар тізімі'):
        send_documents(bot, update)
    elif(update.message.text == 'FAQ'):
        send_faq(bot, update)
    elif(update.message.text == 'Задать вопрос/Сұрақ қою'):
        send_question(bot, update)
        return QUESTION
    elif(update.message.text == 'Назад/Артқа'):
        start(bot, update)
        return TYPE

def first_time_question(bot, update):
    if(update.message.text == 'Да/Иә'):
        send_phone_number(bot, update)
        return REGISTER
    elif(update.message.text == 'Нет/Жоқ'):
        start(bot, update)
        return TYPE

def send_phone_number(bot, update):
    contact_keyboard = telegram.KeyboardButton(text="Отправить номер телефона/Телефон нөмірін жіберу", request_contact=True)
    custom_keyboard = [[contact_keyboard ]]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat_id, text=flag.flagize(':RU:') + " Отправьте нам свои данные" + '\n\n' + flag.flagize(':KZ:') + ' Бізге өз деректеріңізді жіберіңіз', reply_markup=reply_markup)
    reply_markup = telegram.ReplyKeyboardRemove()

def get_user_data(bot, update, user_data, chat_data):
    #print(update.message.contact)
    phone_number = update.message.contact.phone_number
    #phone_number = phone_number.replace("\\", "")
    first_name = update.message.contact.first_name
    #first_name = first_name.replace("\\", "")
    user_id = str(update.message.contact.user_id)
    global user_id_global
    user_id_global = user_id
    #user_id = user_id.replace("\\", "")
    # user_data_dict = {'phone_number': phone_number, 'first_name': first_name, 'user_id': user_id}
    # user_data_json = json.dumps(user_data_dict)
    save_user_data(bot, update, phone_number, first_name, user_id)
    athlete_login(bot, update)
    return ATHLETE

def save_user_data(bot, update, phone_number, first_name, user_id):
    users_ref = ref.child(user_id)
    users_ref.update({
        'phone_number': phone_number,
        'first_name': first_name,
        'user_id': user_id
    })
    
def athlete_auth(bot, update):
    bot.send_chat_action(chat_id=update.message.chat_id, action = telegram.ChatAction.TYPING)
    time.sleep(1)
    custom_keyboard = [['Да/Иә', 'Нет/Жоқ']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat_id, text=flag.flagize(':RU:') + ' Хотите авторизоваться?' + '\n\n' + flag.flagize(':KZ:') + ' Авторланғыңыз келе ме?', reply_markup=reply_markup)
    reply_markup = telegram.ReplyKeyboardRemove()             
    return FIRST

def athlete_choice(bot, update):
    global type_of_user_int
    type_of_user_int = 1
    if(update.message.text == 'Список документов/Құжаттар тізімі'):
        send_documents(bot, update)
    elif(update.message.text == 'Отправить данные/Деректерді жіберу'):
        send_data(bot, update)
        return SEND
    elif(update.message.text == 'FAQ'):
        send_faq(bot, update)
    elif(update.message.text == 'Задать вопрос/Сұрақ қою'):
        send_question(bot, update)
        return QUESTION
    elif(update.message.text == 'Назад/Артқа'):
        start(bot, update)
        return TYPE

def send_data(bot, update):
    bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.ChatAction.TYPING)
    time.sleep(1)
    custom_keyboard = [['Питание/Тамақтану', 'Экскреция/Экскреция'], ['Местоположение/Орналасуы'], ['Назад/Артқа']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat_id, text=flag.flagize(':RU:') + ' Какие данные вы хотите отправить?' + '\n\n' + flag.flagize(':KZ:') + ' Қандай мәліметтерді жібергіңіз келеді?', reply_markup=reply_markup)
    reply_markup = telegram.ReplyKeyboardRemove()

def data_choice(bot, update):
    if(update.message.text == 'Местоположение/Орналасуы'):
        location_keyboard = telegram.KeyboardButton(text="Отправить местоположение/Орналасуын жіберу " + emoji.emojize(':round_pushpin:'), request_location=True)
        custom_keyboard = [[location_keyboard ]]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        bot.send_message(chat_id=update.message.chat_id, text=flag.flagize(':RU:') + " Отправьте нам своё местоположение" + '\n\n' + flag.flagize(':KZ:') + ' Өз орналасуын бізге жіберіңіз', reply_markup=reply_markup)
        reply_markup = telegram.ReplyKeyboardRemove()
        return LOCATION
    elif(update.message.text == 'Питание/Тамақтану'):
        bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.ChatAction.TYPING)
        time.sleep(1)
        bot.send_message(chat_id=update.message.chat_id, text=flag.flagize(':RU:') + ' Что вы ели или употребляли? (напишите через запятую продукты)' + '\n\n' + flag.flagize(':KZ:') + ' Сіз немен тамақтандыңыз немесе қолдандыңыз? (өнімдерді үтір арқылы жазыңыз)', reply_markup = ForceReply(force_reply=True))
        return FOOD
    elif(update.message.text == 'Экскреция/Экскреция'):
        bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.ChatAction.TYPING)
        time.sleep(1)
        bot.send_message(chat_id=update.message.chat_id, text=flag.flagize(':RU:') + ' Опишите ваш процесс экскреции' + '\n\n' + flag.flagize(':KZ:') + ' Сіздің экскреция процесін сипаттаңыз', reply_markup = ForceReply(force_reply=True))
        return EXCRETE
    elif(update.message.text == 'Назад/Артқа'):
        athlete_login(bot, update)
        return ATHLETE

def get_user_food(bot, update, user_data, chat_data):
    food_data = update.message.text
    user_id = str(update.message.chat_id)
    save_food_data(bot, update, food_data, user_id)
    athlete_login(bot, update)
    return ATHLETE

def save_food_data(bot, update, food_data, user_id):
    global ref
    # global user_id_global
    now = datetime.datetime.now()
    food_ref = ref.child(user_id + '/data/' + str(now.strftime("%Y-%m-%d")) + '/' + str(now.strftime("%H:%M") + '/food'))
    food_ref.update({
       'name': food_data
   })

def get_user_excrete(bot, update, user_data, chat_data):
    excrete_data = update.message.text
    user_id = str(update.message.chat_id)
    save_excrete_data(bot, update, excrete_data, user_id)
    athlete_login(bot, update)
    return ATHLETE

def save_excrete_data(bot, update, excrete_data, user_id):
    global ref
    # global user_id_global
    now = datetime.datetime.now()
    excrete_ref = ref.child(user_id + '/data/' + str(now.strftime("%Y-%m-%d")) + '/' + str(now.strftime("%H:%M") + '/excrete'))
    excrete_ref.update({
       'name': excrete_data 
   })

def get_user_location(bot, update, user_data, chat_data):
    latitude = update.message.location.latitude
    longitude = update.message.location.longitude
    user_id = str(update.message.chat_id)
    #print(str(longitude) + " " + str(latitude))
    save_location(bot, update, latitude, longitude, user_id)
    send_data(bot, update)
    return SEND

def save_location(bot, update, latitude, longitude, user_id):
   global ref
   now = datetime.datetime.now()
   #location_ref = ref.child(user_id_global + '/location/' + str(now.strftime("%Y-%m-%d %H:%M")))
   location_ref = ref.child(user_id + '/data/' + str(now.strftime("%Y-%m-%d")) + '/' + str(now.strftime("%H:%M") + '/location'))
   location_ref.update({
       'latitude': latitude,
       'longitude': longitude
   })
    
def send_documents(bot, update):
    bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.ChatAction.TYPING)
    time.sleep(1)
    inline_keyboard = [
        [InlineKeyboardButton('Бланк запроса на Терапевтическое Использование', url='https://drive.google.com/open?id=1zma8UD8YRvMHEMdXlNNK2_Rs4A8Cm4mK')],
        [InlineKeyboardButton('Запрещенный список 2019', url='https://drive.google.com/open?id=1WtA4fXrLcozGTTvaCW9R6jGtCEkuJBIq')],
        [InlineKeyboardButton('Заявление о завершении карьеры', url='https://drive.google.com/open?id=14qKfdlWNfla-LKPsyRQ8PnIgkwU-Or7S')],
        [InlineKeyboardButton('Инструкция по заполнению системы ADAMS', url='https://drive.google.com/open?id=1gt0VL2_HjJmEjwN-aY6JLeEJaCsnkpOU')],
        [InlineKeyboardButton('Международный стандарт по терапевтическому использованию', url='https://drive.google.com/open?id=1R4SGuAaSIpntYEQTzpy6SMpGekBGsK97')],
        [InlineKeyboardButton('Обзор основных изменений в Запрещенном списке 2019', url='https://drive.google.com/open?id=1I3a6QTyVUm6tifrF7XjIBQ6u88-Io9Q0')],
        [InlineKeyboardButton('Положение по терапевтическому использованию',url='https://drive.google.com/open?id=1u_lGQdDbx_sziXIuTouBs0RWoQ0cTm1u')],
        [InlineKeyboardButton('Программа мониторинга 2019', url='https://drive.google.com/open?id=1CrGj-eXl5EqmPxBXyki5m9_PgI9vb_pQ')]
    ]
    inline_markup = telegram.InlineKeyboardMarkup(inline_keyboard)
    bot.send_message(chat_id=update.message.chat_id, text=flag.flagize(':RU:') + ' Отлично! Выберите нужный вам документ' + '\n\n' + flag.flagize(':KZ:') + ' Өте жақсы! Қажетті құжатты таңдаңыз', reply_markup=inline_markup, parse_mode=telegram.ParseMode.MARKDOWN)
    if(type_of_user_int == 0):
        guest_login(bot, update)
    elif(type_of_user_int == 1):
        athlete_login(bot, update)

def send_faq(bot, update):
    bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.ChatAction.TYPING)
    time.sleep(1)
    bot.send_message(chat_id=update.message.chat_id, text='https://telegra.ph/CHasto-zadavaemye-voprosy-FAQ-02-05')
    if(type_of_user_int == 0):
        guest_login(bot, update)
    elif(type_of_user_int == 1):
        athlete_login(bot, update)

def send_question(bot, update):
    bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.ChatAction.TYPING)
    time.sleep(1)
    bot.send_message(chat_id=update.message.chat_id, text=flag.flagize(':RU:') + ' Введите свой вопрос сюда' + '\n\n' + flag.flagize(':KZ:') + ' Өз сұрағыңызды осында енгізіңіз', reply_markup = ForceReply(force_reply=True))

def send_response(bot, update, user_question):
    bot.send_message(chat_id=196842217, text= '*Вопрос пользователя!*\n\n'+ user_question, parse_mode=telegram.ParseMode.MARKDOWN)
    bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.ChatAction.TYPING)
    time.sleep(1)
    bot.send_message(chat_id=update.message.chat_id, text=flag.flagize(':RU:') + ' Мы рассмотрим ваш вопрос!' + '\n\n' + flag.flagize(':KZ:') + ' Біз сіздің сұрағыңызды қарастырамыз!')

def receive_question(bot, update):
    user_question = update.message.text
    send_response(bot, update, user_question)
    if(type_of_user_int == 0):
        guest_login(bot, update)
        return GUEST
    elif(type_of_user_int == 1):
        athlete_login(bot, update)
        return ATHLETE

def send_action(action):
    def decorator(func):
        @wraps(func)
        def command_func(*args, **kwargs):
            bot, update = args
            bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(bot, update, **kwargs)
        return command_func
    
    return decorator

def cancel(bot, update):
    return ConversationHandler.END

def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)

def main():
    # REQUEST_KWARGS={
    #     'proxy_url': 'https://russia.proxytelegram.com:8080/',
    # }
    
    updater = Updater(token=token)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points = [CommandHandler('start', start)],

        states = {
            TYPE: [RegexHandler('^(Спортсмен/Спортшы|Гость/Қонақ)$', type_of_user)],
            #ADMIN: [RegexHandler('^(Список спортсменов|Выход)$', guest_choice)],
            GUEST: [RegexHandler('^(Список документов/Құжаттар тізімі|FAQ|Задать вопрос/Сұрақ қою|Назад/Артқа)$', guest_choice)],
            ATHLETE: [RegexHandler('^(Список документов/Құжаттар тізімі|Отправить данные/Деректерді жіберу|FAQ|Задать вопрос/Сұрақ қою|Назад/Артқа)$', athlete_choice)],
            FIRST: [RegexHandler('^(Да/Иә|Нет/Жоқ)$', first_time_question)],
            REGISTER: [MessageHandler(Filters.contact, get_user_data, pass_user_data=True, pass_chat_data=True)], 
            SEND: [RegexHandler('^(Питание/Тамақтану|Экскреция/Экскреция|Местоположение/Орналасуы|Назад/Артқа)$', data_choice)],
            LOCATION: [MessageHandler(Filters.location, get_user_location, pass_user_data=True, pass_chat_data=True)], 
            QUESTION: [MessageHandler(Filters.text, receive_question)], 
            FOOD: [MessageHandler(Filters.text, get_user_food, pass_user_data=True, pass_chat_data=True)],
            EXCRETE: [MessageHandler(Filters.text, get_user_excrete, pass_user_data=True, pass_chat_data=True)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler)

    dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()