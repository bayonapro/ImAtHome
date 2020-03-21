from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from dotenv import load_dotenv
import os
import requests
import re
import telegram

load_dotenv()

aa_contacts = []
waiting_response = ''
homeOptions = ['Yes', 'Not yet', 'No, I need help']

help_description="""
Hey there 🙋‍♂️🙋‍♀️!
I'm a bot who will contact all of the emergency contacts you gives me whenever you get home or in danger.
The commands are
/start  - Start the way home, let me know your emergency contacts
/home   - Are you at home, on the way or in danger?
/danger - Send DANGER to emergency contacts
/help   - help command
"""

def get_user(obj):
    fn = obj.first_name if obj.first_name != None else ''
    ln = obj.last_name if obj.last_name != None else '' 
    return fn + ln

def start(update, context):
    msg = "Please, send me the contacts you want me to contact."
    help(update, context)
    context.bot.sendMessage(chat_id=update.message.chat_id, text=msg)

def home(update, context):
    message = update.message
    chat_id = message.chat_id
    question = "Are you safe and sound at home?"

    answer1 = telegram.KeyboardButton(text=homeOptions[0])
    answer2 = telegram.KeyboardButton(text=homeOptions[1])
    answer3 = telegram.KeyboardButton(text=homeOptions[2])
    custom_keyboard = [[ answer1 ], [ answer2 ], [ answer3 ]]
    reply_markup = telegram.ReplyKeyboardMarkup(keyboard=custom_keyboard, resize_keyboard=True, one_time_keyboard=True)

    context.bot.sendMessage(chat_id=chat_id, text=question, reply_markup=reply_markup)
    global waiting_response
    waiting_response = 'home'

def danger(update, context):
    context.bot.sendMessage(chat_id=update.message.chat_id, text="Please, send me your live location so I can warn your contacts")

    global waiting_response
    waiting_response = 'home'

def help(update, context):
    context.bot.sendMessage(chat_id=update.message.chat_id, text=help_description)

def sending_help(update, context):
    location = update.message.location 
    user = get_user(update.message.chat)
    for contact in aa_contacts:
        _user = get_user(contact)
        msg = 'Hi {}\n{} is in danger, go help him/her'.format(_user, user)
        context.bot.sendMessage(chat_id=contact.user_id, text=msg)
        context.bot.sendLocation(chat_id=contact.user_id, latitude=location.latitude, longitude=location.longitude)

def send_help(update, context):
    global waiting_response
    if waiting_response == 'home':
        context.bot.sendMessage(chat_id=update.message.chat_id, text="I'M WARNING ALL THE CONTACTS YOU GAVE ME, STAY SAFE PLEASE")
        sending_help(update, context)
        waiting_response = ''
    else:
        context.bot.sendMessage(chat_id=update.message.chat_id, text="Okay, I'll save your current location")

def get_url():
    contents = requests.get('https://random.dog/woof.json').json()
    return contents['url']

def send_ImAtHome(update, context): 
    me = get_user(update.message.chat)

    for contact in aa_contacts:
        user = get_user(contact)
        msg = "Hi there {}!\n{} is at home safe and sound".format(user, me)
        _msg = "{} has recieved I'm at home".format(user)
        context.bot.sendMessage(chat_id=contact.user_id, text=msg)
        context.bot.sendMessage(chat_id=update.message.chat_id, text=_msg)

    url = get_url()
    context.bot.sendMessage(chat_id=update.message.chat_id, text="All your contacts have been informed")
    context.bot.sendPhoto(chat_id=update.message.chat_id, photo=url)
    context.bot.sendMessage(chat_id=update.message.chat_id, text="Be safe 🐶")

def response_of_home(update, context):
    response = update.message.text
    global waiting_response

    if response == homeOptions[0]:
        context.bot.sendMessage(chat_id=update.message.chat_id, text="Great! See you soon!\n(Sending I'm at home to your contacts)")
        send_ImAtHome(update, context)
        waiting_response = ''
    elif response == homeOptions[1]:
        context.bot.sendMessage(chat_id=update.message.chat_id, text="Okay, let me know if you're in trouble 🚶‍♀️🚶‍♂️")
        waiting_response = ''
    else:
        context.bot.sendMessage(chat_id=update.message.chat_id, text="Please, send me your live location so I can warn your contacts")

def message_response(update, context):
    global waiting_response
    if waiting_response == 'home':
        response_of_home(update, context)
    else:
        context.bot.sendMessage(chat_id=update.message.chat_id, text="nothing happened")


def add_contact(update, context):
    contact = update.message.contact
    aa_contacts.append(contact) 
    user = get_user(contact)
    msg = '{}\'s contact saved'.format(user)
    context.bot.sendMessage(chat_id=update.message.chat_id, text=msg)



def main():
    updater = Updater(os.environ['TELEGRAM_TOKEN'], use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('home', home))
    dp.add_handler(CommandHandler('danger', danger))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(MessageHandler(Filters.contact, add_contact))
    dp.add_handler(MessageHandler(Filters.location, send_help))
    dp.add_handler(MessageHandler(Filters.text, message_response))
    updater.start_polling()
    print('Bot is up')
    updater.idle()

if __name__ == '__main__':
    main()