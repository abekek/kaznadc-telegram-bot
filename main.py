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
    custom_keyboard = [['Спортшы/Спортсмен'], ['Қонақ/Гость']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat_id, text=flag.flagize(':KZ:') + ' Сіз кімсіз?' + '\n\n' + flag.flagize(':RU:') +' Кто вы?', reply_markup=reply_markup)
    reply_markup = telegram.ReplyKeyboardRemove()
    return TYPE

def type_of_user(bot, update):
    if(update.message.text == 'Қонақ/Гость'):
        guest_login(bot, update)
        return GUEST
    if(update.message.text == 'Спортшы/Спортсмен'):
        athlete_auth(bot, update)
        return FIRST

def athlete_login(bot, update):
    bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.ChatAction.TYPING)
    time.sleep(1)
    custom_keyboard = [['Құжаттар тізімі/Список документов', 'FAQ'], ['Деректерді жіберу/Отправить данные'], ['Сұрақ қою/Задать вопрос'], ['Артқа/Назад']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat_id, text=flag.flagize(':KZ:') + ' Сіз не істегіңіз келеді?' + '\n\n' + flag.flagize(':RU:') + ' Что вы хотите сделать?', reply_markup=reply_markup)
    reply_markup = telegram.ReplyKeyboardRemove()

def guest_login(bot, update):
    bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.ChatAction.TYPING)
    time.sleep(1)
    custom_keyboard = [['Құжаттар тізімі/Список документов', 'FAQ'], ['Сұрақ қою/Задать вопрос'], ['Артқа/Назад']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat_id, text=flag.flagize(':KZ:') + ' Сіз не істегіңіз келеді?'+ '\n\n' + flag.flagize(':RU:') + ' Что вы хотите сделать?', reply_markup=reply_markup)
    reply_markup = telegram.ReplyKeyboardRemove()

def guest_choice(bot, update):
    global type_of_user_int
    type_of_user_int = 0
    if(update.message.text == 'Құжаттар тізімі/Список документов'):
        send_documents(bot, update)
    elif(update.message.text == 'FAQ'):
        send_faq(bot, update)
    elif(update.message.text == 'Сұрақ қою/Задать вопрос'):
        send_question(bot, update)
        return GUEST
    elif(update.message.text == 'Артқа/Назад'):
        start(bot, update)
        return TYPE

def first_time_question(bot, update):
    if(update.message.text == 'Иә/Да'):
        send_phone_number(bot, update)
        return REGISTER
    elif(update.message.text == 'Жоқ/Нет'):
        start(bot, update)
        return TYPE

def send_phone_number(bot, update):
    contact_keyboard = telegram.KeyboardButton(text="Телефон нөмірін жіберу/Отправить номер телефона", request_contact=True)
    custom_keyboard = [[contact_keyboard ]]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat_id, text=flag.flagize(':KZ:') + ' Бізге өз деректеріңізді жіберіңіз'+ '\n\n' + flag.flagize(':RU:') + " Отправьте нам свои данные", reply_markup=reply_markup)
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
    custom_keyboard = [['Иә/Да', 'Жоқ/Нет']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat_id, text=flag.flagize(':KZ:') + ' Авторланғыңыз келе ме?'+ '\n\n' + flag.flagize(':RU:') + ' Хотите авторизоваться?', reply_markup=reply_markup)
    reply_markup = telegram.ReplyKeyboardRemove()             
    return FIRST

def athlete_choice(bot, update):
    global type_of_user_int
    type_of_user_int = 1
    if(update.message.text == 'Құжаттар тізімі/Список документов'):
        send_documents(bot, update)
    elif(update.message.text == 'Деректерді жіберу/Отправить данные'):
        send_data(bot, update)
        return SEND
    elif(update.message.text == 'FAQ'):
        send_faq(bot, update)
    elif(update.message.text == 'Сұрақ қою/Задать вопрос'):
        send_question(bot, update)
        return ATHLETE
    elif(update.message.text == 'Артқа/Назад'):
        start(bot, update)
        return TYPE

def send_data(bot, update):
    bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.ChatAction.TYPING)
    time.sleep(1)
    custom_keyboard = [['Тамақтану/Питание', 'Экскреция/Экскреция'], ['Орналасуы/Местоположение'], ['Артқа/Назад']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat_id, text=flag.flagize(':RU:') + ' Какие данные вы хотите отправить?' + '\n\n' + flag.flagize(':KZ:') + ' Қандай мәліметтерді жібергіңіз келеді?', reply_markup=reply_markup)
    reply_markup = telegram.ReplyKeyboardRemove()

def data_choice(bot, update):
    if(update.message.text == 'Орналасуы/Местоположение'):
        location_keyboard = telegram.KeyboardButton(text="Орналасуын жіберу/Отправить местоположение " + emoji.emojize(':round_pushpin:'), request_location=True)
        custom_keyboard = [[location_keyboard ]]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        bot.send_message(chat_id=update.message.chat_id, text=flag.flagize(':KZ:') + ' Өз орналасуын бізге жіберіңіз'+ '\n\n' + flag.flagize(':RU:') + " Отправьте нам своё местоположение", reply_markup=reply_markup)
        reply_markup = telegram.ReplyKeyboardRemove()
        return LOCATION
    elif(update.message.text == 'Тамақтану/Питание'):
        bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.ChatAction.TYPING)
        time.sleep(1)
        bot.send_message(chat_id=update.message.chat_id, text=flag.flagize(':KZ:') + ' Сіз немен тамақтандыңыз немесе қолдандыңыз? (өнімдерді үтір арқылы жазыңыз)'+ '\n\n' + flag.flagize(':RU:') + ' Что вы ели или употребляли? (напишите через запятую продукты)', reply_markup = ForceReply(force_reply=True))
        return FOOD
    elif(update.message.text == 'Экскреция/Экскреция'):
        bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.ChatAction.TYPING)
        time.sleep(1)
        bot.send_message(chat_id=update.message.chat_id, text=flag.flagize(':KZ:') + ' Сіздің экскреция процесін сипаттаңыз'+ '\n\n' + flag.flagize(':RU:') + ' Опишите ваш процесс экскреции', reply_markup = ForceReply(force_reply=True))
        return EXCRETE
    elif(update.message.text == 'Артқа/Назад'):
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
    bot.send_message(chat_id=update.message.chat_id, text=flag.flagize(':KZ:') + ' Өте жақсы! Қажетті құжатты таңдаңыз'+ '\n\n' + flag.flagize(':RU:') + ' Отлично! Выберите нужный вам документ', reply_markup=inline_markup, parse_mode=telegram.ParseMode.MARKDOWN)
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

# def send_question(bot, update):
#     bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.ChatAction.TYPING)
#     time.sleep(1)
#     #TODO: send the link
#     bot.send_message(chat_id=update.message.chat_id, text=flag.flagize(':RU:') + ' Введите свой вопрос сюда' + '\n\n' + flag.flagize(':KZ:') + ' Өз сұрағыңызды осында енгізіңіз', reply_markup = ForceReply(force_reply=True))

def send_question(bot, update):
    bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.ChatAction.TYPING)
    time.sleep(1)
    bot.send_message(chat_id=update.message.chat_id, text=flag.flagize(':KZ:') + ' Осы ботты пайдаланып, сұрақ жазыңыз'+ '\n\n' + flag.flagize(':RU:') + ' Задайте свой вопрос этому боту' + '\n\n' + 'https://t.me/kaznadc_support_bot')

# def send_response(bot, update, user_question):
#     bot.send_message(chat_id=196842217, text= '*Вопрос пользователя!*\n\n'+ user_question, parse_mode=telegram.ParseMode.MARKDOWN)
#     bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.ChatAction.TYPING)
#     time.sleep(1)
#     bot.send_message(chat_id=update.message.chat_id, text=flag.flagize(':RU:') + ' Мы рассмотрим ваш вопрос!' + '\n\n' + flag.flagize(':KZ:') + ' Біз сіздің сұрағыңызды қарастырамыз!')

# def receive_question(bot, update):
#     user_question = update.message.text
#     send_response(bot, update, user_question)
#     if(type_of_user_int == 0):
#         guest_login(bot, update)
#         return GUEST
#     elif(type_of_user_int == 1):
#         athlete_login(bot, update)
#         return ATHLETE

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
            TYPE: [RegexHandler('^(Спортшы/Спортсмен|Қонақ/Гость)$', type_of_user)],
            #ADMIN: [RegexHandler('^(Список спортсменов|Выход)$', guest_choice)],
            GUEST: [RegexHandler('^(Құжаттар тізімі/Список документов|FAQ|Сұрақ қою/Задать вопрос|Артқа/Назад)$', guest_choice)],
            ATHLETE: [RegexHandler('^(Құжаттар тізімі/Список документов|Деректерді жіберу/Отправить данные|FAQ|Сұрақ қою/Задать вопрос|Артқа/Назад)$', athlete_choice)],
            FIRST: [RegexHandler('^(Иә/Да|Жоқ/Нет)$', first_time_question)],
            REGISTER: [MessageHandler(Filters.contact, get_user_data, pass_user_data=True, pass_chat_data=True)], 
            SEND: [RegexHandler('^(Тамақтану/Питание|Экскреция/Экскреция|Орналасуы/Местоположение|Артқа/Назад)$', data_choice)],
            LOCATION: [MessageHandler(Filters.location, get_user_location, pass_user_data=True, pass_chat_data=True)], 
            # QUESTION: [MessageHandler(Filters.text, receive_question)], 
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