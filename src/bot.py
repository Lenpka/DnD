from telebot import types
from urllib.request import urlopen
import telebot
import main
import pic
from dotenv import load_dotenv
import os

# загружаем переменные окружения
load_dotenv()

bot_api = os.getenv('TELEGRAM_KEY')
giga_api = os.getenv('GIGA_KEY')
api_key = os.getenv('API_KEY')
secret_key = os.getenv('SECRET_KEY')


bot = telebot.TeleBot(bot_api)


class GameSession:
    def __init__(self):
        self.game_started = False
        self.user_role = None
        self.giga = main.Bot(giga_api)

    def set_role(self, role):
        self.user_role = role

    def start_game(self):
        self.game_started = True

    def reset_game(self):
        self.game_started = False
        self.user_role = None
    
# Похраним пользовательские сессии
sessions = {}

@bot.message_handler(commands=['start']) 
def start(message): 
    if not isinstance(message, types.Message):  
        bot.send_message(message, "An error occurred: invalid message type.")
        return
    chat_id = message.chat.id
    sessions[chat_id] = GameSession()

    main_menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True) 
    item2 = types.KeyboardButton("Начнём игру!") 
    item3 = types.KeyboardButton("Настройки ролей") 
    item4 = types.KeyboardButton("Ссылка на Git") 
    main_menu_markup.add( item2, item3,item4) 
    bot.send_message(message.chat.id, f"Добро пожаловать в портативный DnD, {message.from_user.first_name}! Выбери одну из кнопок ниже после выбора роли.", reply_markup=main_menu_markup)
@bot.message_handler(commands=['history'])  # определяем обработчик команды /history
def get_history(message):
    chat_id = message.chat.id 
    i = 0 # получаем ID чата, из которого была отправлена команда
    messages = bot.history(chat_id, limit=6)  # получаем последние 100 сообщений из чата
    for message in messages:  # проходимся по каждому сообщению из списка сообщений
        bot.send_message(chat_id, f'{i}',message.text) 
        i +=1 # отправляем текст сообщения обратно в чат
@bot.message_handler(content_types=['text'])
def bot_message(message):
    chat_id = message.chat.id

    if chat_id not in sessions:
        sessions[chat_id] = GameSession()
    
    session = sessions[chat_id]

    # TODO добавить обработку в групповом чате
    if message.chat.type != "private":
        return

    if message.text == "Ссылка на Git":
        bot.send_message(chat_id, "https://github.com/Lenpka/DnD/tree/master")

    elif message.text == "Настройки ролей":
        if session.game_started:
            bot.send_message(chat_id, "Вы не можете изменить настройки ролей после начала игры.")
            return
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True) 
        item2 = types.KeyboardButton("Я - ведущий")
        item5 = types.KeyboardButton("Я - игрок") 
        item1 = types.KeyboardButton("Назад") 
        markup.add( item5, item2, item1) 
        bot.send_message(chat_id, "Настройки ролей", reply_markup=markup)

    elif message.text == "Я - ведущий":
        session.set_role(main.role_player)
        bot.send_message(chat_id, "Вы выбрали роль ведущего.")

    elif message.text == "Я - игрок":
        session.set_role(main.role_game_master)
        bot.send_message(chat_id, "Вы выбрали роль игрока.")

    elif message.text == "Начнём игру!":
        if not session.user_role:
            bot.send_message(chat_id, "Пожалуйста, выберите роль перед началом игры.")
            return
        
        session.start_game()
        

        msg = session.giga.newGame(session.user_role)
        markup_p = types.ReplyKeyboardMarkup(resize_keyboard=True) 
        item55 = types.KeyboardButton("Продолжи") 
        item505 = types.KeyboardButton("Выйти в меню")
    
        markup_p.add(item55, item505) 
        bot.send_message(chat_id, "Начнём игру!", reply_markup=markup_p)

        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton("Визуализируй", callback_data=f"visualize:{message.message_id}", message_text=message.text)
        markup.add(button)

        bot.send_message(chat_id, msg, reply_markup=markup)

    elif message.text == "Назад" or message.text == "Выйти в меню":

        markup_set = types.ReplyKeyboardMarkup(resize_keyboard=True) 
        item20 = types.KeyboardButton("Начнём игру!") 
        item39 = types.KeyboardButton("Настройки ролей") 
        item41 = types.KeyboardButton("Ссылка на Git") 
    
        markup_set.add( item41, item20, item39) 
        if message.text == "Назад": 
            bot.send_message(chat_id, "Начнём игру!", reply_markup=markup_set)
        else: 
            bot.send_message(chat_id,  "Выйти в меню",reply_markup=markup_set)

    else:
        if not session.game_started:
            bot.send_message(chat_id, "Игра ещё не началась. Пожалуйста, начните игру сначала.")
            return
        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton("Визуализируй", callback_data=f"visualize:{message.message_id}", message_text=message.text)
        markup.add(button)

        msg = session.giga.answer(message.text)

        # Add inline button for 'Визуализируй' option
        bot.send_message(chat_id, msg, reply_markup=markup)

        ai_msg = session.giga.ai_player_move()
        bot.send_message(chat_id, f"AI Игрок: {ai_msg}", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("visualize:"))
def handle_visualize_callback(call):
    chat_id = call.message.chat.id
    # вот это сможем дальше использовать
    # message_id = call.data.split(":", 1)[1]

    msg = call.message.text
    # message.text
    session = sessions.get(chat_id)
    if not session:
        bot.send_message(chat_id, "Сессия не найдена.")
        return
    
    description = session.giga.getVisualDescription(msg)
    photo = pic.Photo(api_key, secret_key).getPhoto(description)
    # Send the image in memory
    bot.send_photo(chat_id, photo)
    bot.answer_callback_query(call.id, "Обработка завершена!")

if __name__ == '__main__':
    bot.polling(none_stop=True)