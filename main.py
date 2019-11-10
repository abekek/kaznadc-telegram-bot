import telegram
import datetime
import time
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters, ConversationHandler, RegexHandler
from functools import wraps
from telegram import ChatAction, InlineKeyboardButton, ForceReply, KeyboardButton, Contact
import logging
import os
import psycopg2
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import emoji
import flag
from config import token, certificate, db_url
# importing python-telegram-bot, logging, datetime, time, emoji, flag and Firebase libraries

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# setting the logging to see logs in terminal in case of appearing errors

logger = logging.getLogger(__name__)
# initializing logger variable by setting a logger 

TYPE, ATHLETE, GUEST, FIRST, REGISTER, SEND, LOCATION, QUESTION, FOOD = range(9)
# setting the range of variables, which indicate the state of conversation with the bot

cred = credentials.Certificate(certificate)
# Firebase Realtime Database certificate

firebase_admin.initialize_app(cred, {
    'databaseURL': db_url
    # initializing firebase_admin by setting credentials and database url
})
ref = db.reference('users')
# setting the reference for users' database

user_id_global = "" # initializing user_id global variable
type_of_user_int = 0 # initializing type_of_user variable

def start(bot, update):
    # a function, which will start to work after clicking /start in the chat
    bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.ChatAction.TYPING)
    # bot will show its typing process to the user
    time.sleep(1) # the period of time of the typing (1 second)
    custom_keyboard = [['Спортшы/Спортсмен'], ['Қонақ/Гость']] 
    # custom keyboard, which contains athlete and guest buttons
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    # reply markup of the keyboard (will be sended in reply to the /start message) 
    bot.send_message(chat_id=update.message.chat_id, text=flag.flagize(':KZ:') + ' Сіз кімсіз?' + '\n\n' + flag.flagize(':RU:') +' Кто вы?', reply_markup=reply_markup)
    # the message which will be sent with the keyboard (it uses flags to show the language)
    reply_markup = telegram.ReplyKeyboardRemove()
    # removes keyboard after user's response
    return TYPE
    # returns the type of the user and sends to the TYPE state of conversation

def type_of_user(bot, update):
    # a function that will run after returning the TYPE state
    if(update.message.text == 'Қонақ/Гость'):
        # checks if the user is a guest
        guest_login(bot, update)
        # calls login function for a guest
        return GUEST
        # returns GUEST state of conversation
    if(update.message.text == 'Спортшы/Спортсмен'):
        # checks if the user is an athlete
        athlete_auth(bot, update)
        # calls login function for an athlete
        return FIRST
        # returns FIRST state of the conversation

def athlete_login(bot, update):
    # a function that provides options for the athlete
    bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.ChatAction.TYPING)
    # bot will show its typing process to the user
    time.sleep(1) # the period of time of the typing (1 second)
    custom_keyboard = [['Құжаттар тізімі/Список документов', 'FAQ'], ['Деректерді жіберу/Отправить данные'], ['Сұрақ қою/Задать вопрос'], ['Артқа/Назад']]
    # custom keyboard, which contains documents, FAQ, send data, ask a question and go back buttons
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    # reply markup of the keyboard (will be sended in reply to the previous message)
    bot.send_message(chat_id=update.message.chat_id, text=flag.flagize(':KZ:') + ' Сіз не істегіңіз келеді?' + '\n\n' + flag.flagize(':RU:') + ' Что вы хотите сделать?', reply_markup=reply_markup)
    # the message which will be sent with the keyboard (it uses flags to show the language)
    reply_markup = telegram.ReplyKeyboardRemove()
    # removes keyboard after user's response

def guest_login(bot, update):
    # a function that provides options for the guest
    bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.ChatAction.TYPING)
    # bot will show its typing process to the user
    time.sleep(1) # the period of time of the typing (1 second)
    custom_keyboard = [['Құжаттар тізімі/Список документов', 'FAQ'], ['Сұрақ қою/Задать вопрос'], ['Артқа/Назад']]
    # custom keyboard, which contains documents, FAQ, ask a question and go back buttons
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    # reply markup of the keyboard (will be sended in reply to the previous message)
    bot.send_message(chat_id=update.message.chat_id, text=flag.flagize(':KZ:') + ' Сіз не істегіңіз келеді?'+ '\n\n' + flag.flagize(':RU:') + ' Что вы хотите сделать?', reply_markup=reply_markup)
    # the message which will be sent with the keyboard (it uses flags to show the language)
    reply_markup = telegram.ReplyKeyboardRemove()
    # removes keyboard after user's response

def guest_choice(bot, update):
    # a function that operates depending on what choice the guest made
    global type_of_user_int
    # global 'type_of_user_int' variable to set user type in the conversation with the bot
    type_of_user_int = 0
    # setting 'guest' type of user
    if(update.message.text == 'Құжаттар тізімі/Список документов'):
        # checks if the user chose to get the list of documents
        send_documents(bot, update)
        # runs a function to send the list of documents
    elif(update.message.text == 'FAQ'):
        # checks if the user chose get the FAQ
        send_faq(bot, update)
        # runs a function to send the FAQ
    elif(update.message.text == 'Сұрақ қою/Задать вопрос'):
        # checks if the user chose to ask a question
        send_question(bot, update)
        # runs the function to send the question to admins
        return GUEST
        # returns GUEST state of the conversation
    elif(update.message.text == 'Артқа/Назад'):
        # checks if the user wants to go back
        start(bot, update)
        # runs the start function (initial function)
        return TYPE
        # returns TYPE state of the conversation

def first_time_question(bot, update):
    # a function that checks if user wants to authorize
    if(update.message.text == 'Иә/Да'):
        # checks if user responded positively
        send_phone_number(bot, update)
        # runs the function that sends the phone number of the user
        return REGISTER
        # returns REGISTER state of the conversation
    elif(update.message.text == 'Жоқ/Нет'):
        # checks if user responded negatively
        start(bot, update)
        # runs the start function (initial function)
        return TYPE
        # returns TYPE state of the conversation

def send_phone_number(bot, update):
    # a function that allows the user to send phone number to authorize
    contact_keyboard = telegram.KeyboardButton(text="Телефон нөмірін жіберу/Отправить номер телефона", request_contact=True)
    # a customization of the keyboard that will send the phone number of the user
    custom_keyboard = [[contact_keyboard ]]
    # custom keyboard, which contains send the telephone number button
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    # reply markup of the keyboard (will be sended in reply to the previous message)
    bot.send_message(chat_id=update.message.chat_id, text=flag.flagize(':KZ:') + ' Бізге өз деректеріңізді жіберіңіз'+ '\n\n' + flag.flagize(':RU:') + " Отправьте нам свои данные", reply_markup=reply_markup)
    # the message which will be sent with the keyboard (it uses flags to show the language)
    reply_markup = telegram.ReplyKeyboardRemove()
    # removes keyboard after user's response

def get_user_data(bot, update, user_data, chat_data):
    # a function that gets user's data
    phone_number = update.message.contact.phone_number
    # a function that gets user's phone number from sent message
    first_name = update.message.contact.first_name
    # a function that gets user's first name from sent message
    user_id = str(update.message.contact.user_id)
    # gets user_id from the sent message
    global user_id_global
    # global user_id variable initialization
    user_id_global = user_id
    # saves user_id global variable
    save_user_data(bot, update, phone_number, first_name, user_id)
    # runs the function to save user's data
    athlete_login(bot, update)
    # runs previous function to continue conversation
    return ATHLETE
    # returns ATHLETE state of the conversation

def save_user_data(bot, update, phone_number, first_name, user_id):
    # a function that stores user's data into Firebase Realtime Database
    users_ref = ref.child(user_id)
    # creates a path for storing user's data in Firebase Realtime Database
    users_ref.update({
        'phone_number': phone_number,
        'first_name': first_name,
        'user_id': user_id
        # writes user's phone number, first name and user_id into database
    })
    
def athlete_auth(bot, update):
    # a function that will run to allow athlete to authorize
    bot.send_chat_action(chat_id=update.message.chat_id, action = telegram.ChatAction.TYPING)
    # bot will show its typing process to the user
    time.sleep(1) # the period of time of the typing (1 second)
    custom_keyboard = [['Иә/Да', 'Жоқ/Нет']]
    # custom keyboard, which contains yes and no buttons
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    # reply markup of the keyboard (will be sended in reply to the previous message)
    bot.send_message(chat_id=update.message.chat_id, text=flag.flagize(':KZ:') + ' Авторланғыңыз келе ме?'+ '\n\n' + flag.flagize(':RU:') + ' Хотите авторизоваться?', reply_markup=reply_markup)
    # the message which will be sent with the keyboard (it uses flags to show the language)
    reply_markup = telegram.ReplyKeyboardRemove()
    # removes keyboard after user's response        
    return FIRST
    # returns FIRST state of the conversation

def athlete_choice(bot, update):
    # a function that operates depending on what choice the athlete made
    global type_of_user_int
    # global 'type_of_user_int' variable to set user type in the conversation with the bot
    type_of_user_int = 1
    # setting 'athlete' type of user
    if(update.message.text == 'Құжаттар тізімі/Список документов'):
        # checks if the user chose to get the list of documents
        send_documents(bot, update)
        # runs the function to send the list of documents
    elif(update.message.text == 'Деректерді жіберу/Отправить данные'):
        # checks if the user chose to send data
        send_data(bot, update)
        # runs the function to send the data
        return SEND
        # returns SEND state of the conversation
    elif(update.message.text == 'FAQ'):
        # checks if the user chose to get the FAQ
        send_faq(bot, update)
        # runs the function to send the FAQ
    elif(update.message.text == 'Сұрақ қою/Задать вопрос'):
        # checks if the user chose to ask a question
        send_question(bot, update)
        # runs the function to send the question to admins
        return ATHLETE
        # returns ATHLETE state of the conversation
    elif(update.message.text == 'Артқа/Назад'):
        # checks if the user chose to go back
        start(bot, update)
        # runs the start function (initial function)
        return TYPE
        # returns TYPE state of the conversation

def send_data(bot, update):
    # a function that sends athletes' choice of data to send
    bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.ChatAction.TYPING)
    # bot will show its typing process to the user
    time.sleep(1) # the period of time of the typing (1 second)
    custom_keyboard = [['Тамақтану/Питание'], ['Орналасуы/Местоположение'], ['Артқа/Назад']]
    # custom keyboard, which contains food data, location and go back buttons
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    # reply markup of the keyboard (will be sended in reply to the previous message)
    bot.send_message(chat_id=update.message.chat_id, text=flag.flagize(':RU:') + ' Какие данные вы хотите отправить?' + '\n\n' + flag.flagize(':KZ:') + ' Қандай мәліметтерді жібергіңіз келеді?', reply_markup=reply_markup)
    # the message which will be sent with the keyboard (it uses flags to show the language)
    reply_markup = telegram.ReplyKeyboardRemove()
    # removes keyboard after user's response

def data_choice(bot, update):
    # a function that operates depending on what choice the user made
    if(update.message.text == 'Орналасуы/Местоположение'):
        # checks if the user chose to send location
        location_keyboard = telegram.KeyboardButton(text="Орналасуын жіберу/Отправить местоположение " + emoji.emojize(':round_pushpin:'), request_location=True)
        # customization of the keyboard to send the location of user
        custom_keyboard = [[location_keyboard ]]
        # places the location keyboard on the main custom keyboard
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        # reply markup of the keyboard (will be sended in reply to the previous message)
        bot.send_message(chat_id=update.message.chat_id, text=flag.flagize(':KZ:') + ' Өз орналасуын бізге жіберіңіз'+ '\n\n' + flag.flagize(':RU:') + " Отправьте нам своё местоположение", reply_markup=reply_markup)
        # the message which will be sent with the keyboard (it uses flags to show the language)
        reply_markup = telegram.ReplyKeyboardRemove()
        # removes keyboard after user's response
        return LOCATION
        # returns LOCATION state of the conversation
    elif(update.message.text == 'Тамақтану/Питание'):
        # checks if the user chose to send food data
        bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.ChatAction.TYPING)
        # bot will show its typing process to the user
        time.sleep(1) # the period of time of the typing (1 second)
        bot.send_message(chat_id=update.message.chat_id, text=flag.flagize(':KZ:') + ' Сіз немен тамақтандыңыз немесе қолдандыңыз? (өнімдерді үтір арқылы жазыңыз)'+ '\n\n' + flag.flagize(':RU:') + ' Что вы ели или употребляли? (напишите через запятую продукты)', reply_markup = ForceReply(force_reply=True))
        # the message which will be sent with the keyboard (it uses flags to show the language). Force Reply will bind the user to type the reply to the message
        return FOOD
        # returns FOOD state of the conversation

    # elif(update.message.text == 'Экскреция/Экскреция'):
    #     bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.ChatAction.TYPING)
    #     time.sleep(1)
    #     bot.send_message(chat_id=update.message.chat_id, text=flag.flagize(':KZ:') + ' Сіздің экскреция процесін сипаттаңыз'+ '\n\n' + flag.flagize(':RU:') + ' Опишите ваш процесс экскреции', reply_markup = ForceReply(force_reply=True))
    #     return EXCRETE

    elif(update.message.text == 'Артқа/Назад'):
        # checks if the user chose to go back in the conversation
        athlete_login(bot, update)
        # runs previous function to continue conversation
        return ATHLETE
        # returns ATHLETE state of conversation

def get_user_food(bot, update, user_data, chat_data):
    # a function that gets user's food data from sent message
    food_data = update.message.text
    # saves food data into a variable 
    user_id = str(update.message.chat_id)
    # gets user_id from the sent message
    save_food_data(bot, update, food_data, user_id)
    # runs another function to save the food data in database
    athlete_login(bot, update)
    # runs previous function to continue conversation
    return ATHLETE
    # returns ATHLETE state of conversation

def save_food_data(bot, update, food_data, user_id):
    # a function that saves user's food data into Firebase Realtime Database
    global ref
    # global 'ref' variable - provides a reference for the database 
    now = datetime.datetime.now()
    # saves current datetime
    food_ref = ref.child(user_id + '/data/' + str(now.strftime("%Y-%m-%d")) + '/' + str(now.strftime("%H:%M") + '/food'))
    # creates a path for storing food data in Firebase Realtime Database
    food_ref.update({
       'name': food_data
       # writes food name into database
   })

# def get_user_excrete(bot, update, user_data, chat_data):
#     excrete_data = update.message.text
#     user_id = str(update.message.chat_id)
#     save_excrete_data(bot, update, excrete_data, user_id)
#     athlete_login(bot, update)
#     return ATHLETE

# def save_excrete_data(bot, update, excrete_data, user_id):
#     global ref
#     # global user_id_global
#     now = datetime.datetime.now()
#     excrete_ref = ref.child(user_id + '/data/' + str(now.strftime("%Y-%m-%d")) + '/' + str(now.strftime("%H:%M") + '/excrete'))
#     excrete_ref.update({
#        'name': excrete_data 
#    })

def get_user_location(bot, update, user_data, chat_data):
    # a function that gets user's location from sent message
    latitude = update.message.location.latitude
    longitude = update.message.location.longitude
    # saves latitude and longitude into two separate variables 
    user_id = str(update.message.chat_id)
    # gets user_id from the sent message
    save_location(bot, update, latitude, longitude, user_id)
    # runs another function to save the location in database
    send_data(bot, update)
    # runs previous function to continue conversation
    return SEND
    # returns SEND state of the conversation

def save_location(bot, update, latitude, longitude, user_id):
    # a function that saves user's location into Firebase Realtime Database
    global ref
    # global 'ref' variable - provides a reference for the database 
    now = datetime.datetime.now()
    # saves current datetime
    location_ref = ref.child(user_id + '/data/' + str(now.strftime("%Y-%m-%d")) + '/' + str(now.strftime("%H:%M") + '/location'))
    # creates a path for storing location in Firebase Realtime Database
    location_ref.update({
       'latitude': latitude,
       'longitude': longitude
       # writes location (latitude and longitude) into database
    })
    
def send_documents(bot, update):
    # a function that sends documents to the user
    bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.ChatAction.TYPING)
    # bot will show its typing process to the user
    time.sleep(1) # the period of time of the typing (1 second)
    inline_keyboard = [
        [InlineKeyboardButton('Бланк запроса на Терапевтическое Использование', url='https://drive.google.com/open?id=1zma8UD8YRvMHEMdXlNNK2_Rs4A8Cm4mK')],
        [InlineKeyboardButton('Запрещенный список 2019', url='https://drive.google.com/open?id=1WtA4fXrLcozGTTvaCW9R6jGtCEkuJBIq')],
        [InlineKeyboardButton('Заявление о завершении карьеры', url='https://drive.google.com/open?id=14qKfdlWNfla-LKPsyRQ8PnIgkwU-Or7S')],
        [InlineKeyboardButton('Инструкция по заполнению системы ADAMS', url='https://drive.google.com/open?id=1gt0VL2_HjJmEjwN-aY6JLeEJaCsnkpOU')],
        [InlineKeyboardButton('Международный стандарт по терапевтическому использованию', url='https://drive.google.com/open?id=1R4SGuAaSIpntYEQTzpy6SMpGekBGsK97')],
        [InlineKeyboardButton('Обзор основных изменений в Запрещенном списке 2019', url='https://drive.google.com/open?id=1I3a6QTyVUm6tifrF7XjIBQ6u88-Io9Q0')],
        [InlineKeyboardButton('Положение по терапевтическому использованию',url='https://drive.google.com/open?id=1u_lGQdDbx_sziXIuTouBs0RWoQ0cTm1u')],
        [InlineKeyboardButton('Программа мониторинга 2019', url='https://drive.google.com/open?id=1CrGj-eXl5EqmPxBXyki5m9_PgI9vb_pQ')],
        [InlineKeyboardButton('2020-Prohibited-List-RUS', url='https://drive.google.com/open?id=1sgEq5mdVykQNPF2M0IAih0PlpJjxYmVE')],
        [InlineKeyboardButton('Программа мониторинга 2020', url='https://drive.google.com/open?id=1MjQWARhEnsoPSTZpHjPZmB_sEzFJw2nQ')]
    ]
    # an array of inline keyboard elements (documents)
    inline_markup = telegram.InlineKeyboardMarkup(inline_keyboard)
    # inline keyboard markup for downloadable documents
    bot.send_message(chat_id=update.message.chat_id, text=flag.flagize(':KZ:') + ' Өте жақсы! Қажетті құжатты таңдаңыз'+ '\n\n' + flag.flagize(':RU:') + ' Отлично! Выберите нужный вам документ', reply_markup=inline_markup, parse_mode=telegram.ParseMode.MARKDOWN)
    # the message which will be sent with the keyboard (it uses flags to show the language). Markdown mode in ON
    if(type_of_user_int == 0):
        # checks if user is a guest
        guest_login(bot, update)
        # runs the login function for guest
    elif(type_of_user_int == 1):
        # checks if user is an athlete
        athlete_login(bot, update)
        # runs the login function for athlete

def send_faq(bot, update):
    # a function that sends FAQ to the user
    bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.ChatAction.TYPING)
    # bot will show its typing process to the user
    time.sleep(1) # the period of time of the typing (1 second)
    bot.send_message(chat_id=update.message.chat_id, text='https://telegra.ph/CHasto-zadavaemye-voprosy-FAQ-02-05')
    # the message which will be sent with the keyboard
    if(type_of_user_int == 0):
        # checks if user is a guest
        guest_login(bot, update)
        # runs the login function for guest
    elif(type_of_user_int == 1):
        # checks if user is an athlete
        athlete_login(bot, update)
        # runs the login function for athlete

def send_question(bot, update):
    # a function that sends the link for asking the question from admins
    bot.send_chat_action(chat_id=update.message.chat_id , action = telegram.ChatAction.TYPING)
    # bot will show its typing process to the user
    time.sleep(1) # the period of time of the typing (1 second)
    bot.send_message(chat_id=update.message.chat_id, text=flag.flagize(':KZ:') + ' Осы ботты пайдаланып, сұрақ жазыңыз'+ '\n\n' + flag.flagize(':RU:') + ' Задайте свой вопрос этому боту' + '\n\n' + 'https://t.me/kaznadc_support_bot')
    # the message which will be sent with the keyboard (it uses flags to show the language)

def send_action(action):
    # a function that shows the action of the bot ('typing)
    # this parametrized decorator allows to signal different actions depending on the type of response of the bot. This way users will have similar feedback from the bot as they would from a real human.
    def decorator(func):
        @wraps(func)
        def command_func(*args, **kwargs):
            bot, update = args
            bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(bot, update, **kwargs)
        return command_func
    
    return decorator

def cancel(bot, update):
    # a funcion that will end the conversation with the user 
    return ConversationHandler.END

def error(bot, update, error):
    # a function that will print errors to logs
    logger.warning('Update "%s" caused error "%s"', update, error)

def main():
    # main method that will run initially
    updater = Updater(token=token) # setting the token of Telegram to the updater
    dispatcher = updater.dispatcher # setting updater dispatcher

    conv_handler = ConversationHandler(
        # creating a conversation handler, which will handle different commands
        entry_points = [CommandHandler('start', start)], 
        # the /start command which will lead to 'start' method (function)

        states = {
            # states of the conversation, which will handle messages of the user through Regular Expresions and in result, run methods to continue the conversation
            TYPE: [RegexHandler('^(Спортшы/Спортсмен|Қонақ/Гость)$', type_of_user)],
            GUEST: [RegexHandler('^(Құжаттар тізімі/Список документов|FAQ|Сұрақ қою/Задать вопрос|Артқа/Назад)$', guest_choice)],
            ATHLETE: [RegexHandler('^(Құжаттар тізімі/Список документов|Деректерді жіберу/Отправить данные|FAQ|Сұрақ қою/Задать вопрос|Артқа/Назад)$', athlete_choice)],
            FIRST: [RegexHandler('^(Иә/Да|Жоқ/Нет)$', first_time_question)],
            REGISTER: [MessageHandler(Filters.contact, get_user_data, pass_user_data=True, pass_chat_data=True)], 
            SEND: [RegexHandler('^(Тамақтану/Питание|Орналасуы/Местоположение|Артқа/Назад)$', data_choice)],
            LOCATION: [MessageHandler(Filters.location, get_user_location, pass_user_data=True, pass_chat_data=True)], 
            FOOD: [MessageHandler(Filters.text, get_user_food, pass_user_data=True, pass_chat_data=True)]
            # EXCRETE: [MessageHandler(Filters.text, get_user_excrete, pass_user_data=True, pass_chat_data=True)]
        },

        fallbacks=[CommandHandler('cancel', cancel)] 
        # the /cancel command, which will end the conversation and return it to initial state
    )

    dispatcher.add_handler(conv_handler)
    # adding a handler to the dispatcher

    dispatcher.add_error_handler(error)
    # adding an error handler to the dispatcher

    updater.start_polling()
    # starting the updater to run code
    updater.idle()
    # preventing the bot to stop or pause

if __name__ == '__main__':
    main()
    # setting the 'main' method as initial 