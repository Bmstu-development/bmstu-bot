from datetime import datetime
import telebot
import time
from flask import Flask

from parsers.web_parser import get_link
from parsers.calendar_parser import get_schedule_day, get_schedule_week, compare_schedule_date
from parallel_processing.pp_decorators import separated_thread
from db_control.init import create


def telegram_bot(token):
    # app = Flask(__name__)
    bot = telebot.TeleBot(token)

    # create()

    @bot.message_handler(commands=['start'])
    @separated_thread
    def command_start(message):
        bot.send_message(message.chat.id, 'Здравствуйте!\nВведите /help, чтобы увидеть список команд')

    @bot.message_handler(commands=['help'])
    @separated_thread
    def command_help(message):
        bot.send_message(
            message.chat.id,
            '/help возвращает список команд\n'
            '/today\_schedule ```[group]``` возвращает расписание на текущий день, если группа не указана, будет выбрана ваша группа\n'
            '/date\_schedule ```[group][date]``` возвращает расписание на указанную дату, если группа не указана, будет выбрана ваша группа\n'
            '/week\_schedule ```[group]``` возвращает расписание с текущего дня до конца недели, если группа не указана, будет выбрана ваша группа\n'
            '/change\_group ```[group]``` запоминает вашу группу\n'
            '/remove\_group забывает вашу группу\n'
            '/compare\_schedule\_date ```[group1][group2][date]```\n'
            'compare\_schedule\_today ```[group1][group2]```\n',
            parse_mode='Markdown'
        )

    @bot.message_handler(commands=['today_schedule'])
    @separated_thread
    def command_today_schedule(message):
        args = message.text.split()[1:]
        if len(args) != 1:
            bot.send_message(message.chat.id, 'Команда имеет один обязательный аргумент - номер группы '
                                              '(ИУ5-35Б, Э4-11А и тп)')
            return
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
                        answer += f'\n{lesson}\t\t{" ".join(timetable[lesson]).replace("None", "")}'
            bot.send_message(message.chat.id, answer, parse_mode='Markdown', disable_web_page_preview=True)
        else:
            bot.send_message(message.chat.id, pair[1])

    @bot.message_handler(commands=['date_schedule'])
    @separated_thread
    def command_date_schedule(message):
        args = message.text.split()[1:]
        if len(args) != 2:
            bot.send_message(message.chat.id, 'Команда имеет два обязательных аргумента: номер группы (например, '
                                              'МТ6-11Б) и дату (формат: дд.мм.гг)')
            return
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
                            answer += f'\n{lesson}\t\t{" ".join(timetable[lesson]).replace("None", "")}'
                bot.send_message(message.chat.id, answer, parse_mode='Markdown', disable_web_page_preview=True)
            except ValueError:
                bot.send_message(message.chat.id, 'Неверный формат даты. Требуется дд.мм.гг')
        else:
            bot.send_message(message.chat.id, pair[1])

    @bot.message_handler(commands=['week_schedule'])
    @separated_thread
    def command_week_schedule(message):
        args = message.text.split()[1:]
        if len(args) != 1:
            bot.send_message(message.chat.id, 'Команда имеет один обязательный аргумент - номер группы '
                                              '(ИУ8-15, Э4-11А и тп)')
            return
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

    @bot.message_handler(commands=['change_group'])
    @separated_thread
    def command_change_group(message):
        args = message.text.split()[1:]
        if len(args) != 1:
            bot.send_message(message.chat.id, 'Команда имеет один обязательный аргумент - номер группы '
                                              '(ИУ8-15, Э4-11А и тп)')
        else:
            check = get_link(args[0].upper())
            if not check[0]:
                bot.send_message(message.chat.id, check[1])
            else:
                bot.send_message(message.chat.id, 'Группа записана')

    @bot.message_handler(commands=['remove_group'])
    @separated_thread
    def command_remove_group(message):
        bot.send_message(message.chat.id, 'Записанная группа была удалена')

    # Здесь получилось так, что каким бы аргумент с номером группы ни был (корректный, например, ИУ8-45 или нет,
    # например, иу-), она будет искаться. Если не найдется, будет ответ "группа не найдена!", хотя раньше мог быть ответ
    # "неверный формат группы...". Это следует исправить и сделать так, чтобы всегда ответ при одинаковых данных был
    # одинаковым
    @bot.message_handler(commands=['compare_schedule_date'])
    @separated_thread
    def command_compare_schedule_date(message):
        args = message.text.split()[1:]
        if len(args) != 3:
            bot.send_message(message.chat.id, 'Команда имеет три обязательных аргумента: номер первой группы, номер '
                                              'второй группы, дата')
        else:
            first_pair = get_link(args[0].upper())
            if first_pair[0]:
                first_link = first_pair[1]
                second_pair = get_link(args[1].upper())
                if second_pair[0]:
                    second_link = second_pair[1]
                    try:
                        date = datetime.strptime(args[2], '%d.%m.%y')
                        result = compare_schedule_date((first_link, second_link), date)
                        if result is not None:
                            answer = f"Расписание [{args[0].upper()}]({first_pair[1]}), расписание " \
                                     f"[{args[1].upper()}]({second_pair[1]}).\n\n" \
                                     f"Сравнение на {date.date().strftime('%d.%m.%y')}:\n"
                            for type_ in result:
                                answer += f'{type_}:\n'
                                if not len(result[type_]):
                                    answer += 'Нет\n\n'
                                for item in result[type_]:
                                    if type(item) is not str:
                                        answer += ' '.join(tuple(item))
                                    else:
                                        answer += item
                                    answer += '\n'
                                answer += '\n'
                            bot.send_message(message.chat.id, answer, parse_mode='Markdown',
                                             disable_web_page_preview=True)
                        else:
                            bot.send_message(message.chat.id, 'Не удалось сравнить расписания')
                    except ValueError:
                        bot.send_message(message.chat.id, 'Неверный формат даты. Требуется дд.мм.гг')
                else:
                    bot.send_message(message.chat.id, f'Группа {args[1]} не найдена!')
            else:
                bot.send_message(message.chat.id, f'Группа {args[0]} не найдена!')

    @bot.message_handler(commands=['compare_schedule_today'])
    @separated_thread
    def command_compare_schedule_date(message):
        args = message.text.split()[1:]
        if len(args) != 2:
            bot.send_message(message.chat.id, 'Команда имеет два обязательных аргумента: номер первой группы, номер '
                                              'второй группы')
        else:
            pass

    # bot.remove_webhook()
    # bot.set_webhook(f'https://0.0.0.0:8443/{token}')
    # app.run('0.0.0.0', 8443)

    while True:
        try:
            bot.polling(timeout=100)
        except Exception as e:
            print(e)
            time.sleep(15)
