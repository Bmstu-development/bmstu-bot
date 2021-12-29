from datetime import datetime
import telebot

from parsers.web_parser import get_link
from parsers.calendar_parser import get_schedule_day, get_schedule_week


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
                answer = f"Расписание доступно по [ссылке]({link})\n\n{datetime.now().strftime('%d.%m.%y')}:"
                timetable = get_schedule_day(link)
                if timetable is None:
                    answer += '\nНевозможно отобразить расписание. Воспользуйтесь ссылкой выше.'
                elif not len(timetable):
                    answer += '\nВ этот день занятий нет\n'
                else:
                    if type(timetable) is str:
                        answer += '\n' + timetable
                    else:
                        for lesson in sorted(timetable):
                            answer += f'\n{lesson}\t\t{timetable[lesson]}'
                bot.send_message(message.chat.id, answer, parse_mode='Markdown', disable_web_page_preview=True)
            else:
                bot.send_message(message.chat.id, pair[1])

    @bot.message_handler(commands=['date_schedule'])
    def command_date_schedule(message):
        args = message.text.split()[1:]
        if len(args) != 2:
            bot.send_message(message.chat.id, 'Команда имеет два обязательных аргумента: номер группы (например, '
                                              'МТ6-11Б) и дату (формат: дд.мм.гг)')
        else:
            pair = get_link(args[0].upper())
            if pair[0]:
                link = pair[1]
                try:
                    date = datetime.strptime(args[1], '%d.%m.%y')
                    answer = f"Расписание доступно по [ссылке]({link})\n\n{date.date().strftime('%d.%m.%y')}:"
                    timetable = get_schedule_day(link, date)
                    if timetable is None:
                        answer += '\nНевозможно отобразить расписание. Воспользуйтесь ссылкой выше.'
                    elif not len(timetable):
                        answer += '\nВ этот день занятий нет\n'
                    else:
                        if type(timetable) is str:
                            answer += '\n' + timetable
                        else:
                            for lesson in sorted(timetable):
                                answer += f'\n{lesson}\t\t{timetable[lesson]}'
                    bot.send_message(message.chat.id, answer, parse_mode='Markdown', disable_web_page_preview=True)
                except ValueError:
                    bot.send_message(message.chat.id, 'Неверный формат даты. Требуется дд.мм.гг')
            else:
                bot.send_message(message.chat.id, pair[1])

    @bot.message_handler(commands=['week_schedule'])
    def command_week_schedule(message):
        args = message.text.split()[1:]
        if len(args) != 1:
            bot.send_message(message.chat.id, 'Команда имеет один обязательный аргумент - номер группы '
                                              '(ИУ8-15, Э4-11А и тп)')
        else:
            pair = get_link(args[0].upper())
            if pair[0]:
                link = pair[1]
                answer = f'Расписание доступно по [ссылке]({link})\n'
                timetable = get_schedule_week(link)
                if timetable is None:
                    answer += '\nНевозможно отобразить расписание. Воспользуйтесь ссылкой выше.'
                else:
                    for date in timetable:
                        answer += '\n' + date
                        if type(timetable[date]) is dict:
                            if not len(timetable[date]):
                                answer += '\nВ этот день занятий нет\n'
                                continue
                            for lesson in sorted(timetable[date]):
                                answer += f'\n{lesson}\t\t{timetable[date][lesson]}'
                        else:
                            answer += '\n' + timetable[date]
                        answer += '\n'
                bot.send_message(message.chat.id, answer, parse_mode='Markdown', disable_web_page_preview=True)
            else:
                bot.send_message(message.chat.id, pair[1])

    bot.polling(timeout=100)
