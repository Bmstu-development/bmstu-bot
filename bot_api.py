import telebot
from schedule.parser import get_schedule


def telegram_bot(token):
    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=['start'])
    def command_start(message):
        bot.send_message(message.chat.id, 'Hello!')

    @bot.message_handler(commands=['auth'])
    def command_auth(message):
        reg_data = message.text.split()[1:]
        if len(reg_data) != 2:
            bot.send_message(message.chat.id, 'Wrong input data. This command should have two arguments: login and '
                                              'password')
        else:
            bot.send_message(message.chat.id, 'You have successfully authorized!')
            print(reg_data)

    @bot.message_handler(commands=['today_schedule'])
    def command_today_schedule(message):
        args = message.text.split()[1:]
        if len(args) != 1:
            bot.send_message(message.chat.id, 'Wrong input data. This command requires one argument: name of group'
                                              ' (ИУ5-35Б, Э4-11А, etc)')
        else:
            answer = get_schedule(args[0].upper())
            bot.send_message(message.chat.id, answer)

    bot.polling(timeout=100)
