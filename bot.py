from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ChatAction
import logging
import subprocess


def start(bot, update):  # Function for the start command
    bot.send_message(chat_id=update.message.chat_id, text="Отправьте мне 3 фотографий феросплава и я такое выдам")


def unknown(bot, update):  # Function for the unknown commands
    bot.send_message(chat_id=update.message.chat_id, text="Извините, но данная команда не поддерживается")


def nonImage(bot, update):  # Function for the non-image messages
    bot.send_message(chat_id=update.message.chat_id, text="Я могу обрабатывать только фотографий")


def image(bot, update):  # Function for the image messages
    global dictionary_of_users
    if update.message.chat_id not in dictionary_of_users:
        dictionary_of_users[update.message.chat_id] = 0
    if dictionary_of_users[update.message.chat_id] == 0:
        bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
        bot.getFile(update.message.photo[-1].file_id).download('img1.jpg')
        dictionary_of_users[update.message.chat_id] = 1
        subprocess.call("python label_image.py", shell=True)
        bot.send_message(chat_id=update.message.chat_id, text="Обрабатываю первую фотографию")
    elif dictionary_of_users[update.message.chat_id] == 1:
        bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
        bot.getFile(update.message.photo[-1].file_id).download('img2.jpg')
        dictionary_of_users[update.message.chat_id] = 2
        subprocess.call("python label_image2.py", shell=True)
        bot.send_message(chat_id=update.message.chat_id, text="Обрабатываю вторую фотографию")
    elif dictionary_of_users[update.message.chat_id] == 2:
        bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
        bot.getFile(update.message.photo[-1].file_id).download('img3.jpg')
        dictionary_of_users[update.message.chat_id] = 0
        bot.send_message(chat_id=update.message.chat_id, text="Осталась последняя, оидайте")
        bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)        
        subprocess.call("python label_image3.py", shell=True)
        return_from_processing_data = processing_data()
        bot.send_message(chat_id=update.message.chat_id, text="Ваш образец " + return_from_processing_data[0] + ", с точностью: " + str(return_from_processing_data[1]))


def processing_data():
    first_output = open('output_file.txt', 'r')
    second_output = open('output_file2.txt', 'r')
    third_output = open('output_file3.txt', 'r')
    firstlines = first_output.read().split('\n')
    secondlines = second_output.read().split('\n')
    thirdlines = third_output.read().split('\n')
    high_num = 0.0
    medium_num = 0.0
    low_num = 0.0
    high_percent = 0.0
    medium_percent = 0.0
    low_percent = 0.0
    high_ave = 0.0
    medium_ave = 0.0
    low_ave = 0.0
    if firstlines[0] == 'high':
        high_num = 1
        high_percent = float(firstlines[1])
    elif firstlines[0] == 'medium':
        medium_num = 1
        medium_percent = float(firstlines[1])
    else:
        low_num = 1   
        low_percent = float(firstlines[1])
    if secondlines[0] == 'high':
        high_num += 1
        high_percent += float(secondlines[1])
    elif secondlines[0] == 'medium':
        medium_num += 1
        medium_percent += float(secondlines[1])
    else:
        low_num += 1   
        low_percent += float(secondlines[1])
    if thirdlines[0] == 'high':
        high_num += 1
        high_percent += float(thirdlines[1])
    elif thirdlines[0] == 'medium':
        medium_num += 1
        medium_percent += float(thirdlines[1])
    else:
        low_num += 1   
        low_percent += float(thirdlines[1]) 
    if high_num > 0:
        high_ave = high_percent / high_num
    if medium_num > 0:
        medium_ave = medium_percent / medium_num
    if low_num > 0:
        low_ave = low_percent / low_num
    if max(high_ave, medium_ave, low_ave) == high_ave:
        final_value = ['высокоуглеродистый', high_ave]
    elif max(high_ave, medium_ave, low_ave) == medium_ave:
        final_value = ['среднеуглеродистый', medium_ave]
    else:
        final_value = ['низкоуглеродистый', low_ave]
    return final_value



# Setting an updater and intruducing a dispatcher
updater = Updater(token='551638500:AAGcNgDtUwRM93fqb9U9vFHUwG-HQa8YaU4')
dispatcher = updater.dispatcher
dictionary_of_users = dict()

# Setting up a logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Introducing start handler
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

# Introducing unknown handler
unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)

# Introducing image handler
image_handler = MessageHandler(Filters.photo, image)
dispatcher.add_handler(image_handler)

# Introducing non-image message handler
nonImage_handler = MessageHandler(~Filters.photo, nonImage)
dispatcher.add_handler(nonImage_handler)

# Runing the bot
updater.start_polling()

# To stop the bot:
# updater.stop()
# https://github.com/simplyalde