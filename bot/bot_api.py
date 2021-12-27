from datetime import datetime
import telebot

from parsers.web_parser import get_link
from parsers.calendar_parser import get_schedule_today


def telegram_bot(token):
    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=['start'])
    def command_start(message):
        bot.send_message(message.chat.id, 'Hello!')

    # @bot.message_handler(commands=['auth'])
    # def command_auth(message):
    #     reg_data = message.text.split()[1:]
    #     if len(reg_data) != 2:
    #         bot.send_message(message.chat.id, 'Wrong input data. This command should have two arguments: login and '
    #                                           'password')
    #     else:
    #         bot.send_message(message.chat.id, 'You have successfully authorized!')
    #         print(reg_data)

    @bot.message_handler(commands=['today_schedule'])
    def command_today_schedule(message):
        args = message.text.split()[1:]
        if len(args) != 1:
            bot.send_message(message.chat.id, 'Команда имеет один обязательный аргумент - номер группы '
                                              '(ИУ5-35Б, Э4-11А и тп)')
        else:
            pair = get_link(args[0].upper())
            if pair[0]:
                link = pair[1]
                answer = f'Расписание доступно по [ссылке]({link})\n'
                timetable = get_schedule_today(link)
                if timetable is None:
                    answer += '\nНевозможно отобразить расписание. Воспользуйтесь ссылкой выше.'
                answer += f"\n{datetime.now().strftime('%d.%m.%y')}:"
                if type(timetable) is str:
                    answer += '\n' + timetable
                else:
                    for lesson in sorted(timetable):
                        answer += f'\n{lesson}\t\t{timetable[lesson]}'
                bot.send_message(message.chat.id, answer, parse_mode='Markdown', disable_web_page_preview=True)
            else:
                bot.send_message(message.chat.id, pair[1])

    bot.polling(timeout=100)
