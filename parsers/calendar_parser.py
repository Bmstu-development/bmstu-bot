from icalendar import Calendar
from datetime import datetime, timedelta

from parsers.web_parser import get_ics


# def get_dict(ics):
#     pass
#

# Функция получения расписания на текущие сутки. Получается содержимое ics-файла и начинается обход. Учитывается
# кратность недели, физра (Измайлово и СК), выходные дни
def get_schedule_day(url, date=datetime.now()):
    ics_string, parity = get_ics(url)
    if ics_string is not None:
        week = Calendar.from_ical(ics_string)
        timetable = {}
        for component in week.walk():
            if component.name == "VEVENT":
                dt = component.get('dtstart').dt
                if dt.weekday() == date.weekday():
                    lesson_name = str(component.get('summary'))
                    if 'Самостоятельная работа' in lesson_name:
                        return 'В этот день занятий нет'
                    if 'Измайлово' in lesson_name:
                        lesson_name = lesson_name[1:]
                        dt_start = datetime.strptime(lesson_name[:lesson_name.find(' ')], '%H.%M')
                        dt_end = dt_start + timedelta(minutes=95)
                        lesson_name = lesson_name[lesson_name.find(' '):]
                    elif 'Элективный' in lesson_name:
                        change_time = {
                            '8:30': '8:15',
                            '10:15': '10:00',
                            '12:00': '12:20',
                            '13:50': '14:05',
                            '15:40': '15:50',
                            '17:25': '17:30',
                        }
                        dt_start = (dt + timedelta(hours=3)).time()
                        for time in change_time:
                            if datetime.strptime(time, '%H:%M').time() == dt_start:
                                dt_start = datetime.strptime(change_time[time], '%H:%M')
                                dt_end = dt_start + timedelta(minutes=90)
                                break
                    else:
                        dt_start = dt + timedelta(hours=3)
                        dt_end = component.get('dtend').dt + timedelta(hours=3)
                    duration = f"{dt_start.strftime('%H:%M')}-{dt_end.strftime('%H:%M')}"
                    freq = dict(component.get('rrule'))['INTERVAL'][0]
                    if freq == 1:
                        timetable[duration] = (lesson_name, str(component.get('LOCATION')))
                    elif freq == 2 and (date.date() - dt_start.date()).days % 2 == 0:
                        timetable[duration] = (lesson_name, str(component.get('LOCATION')))
        return timetable
    return None


def get_schedule_week(url, date=datetime.now()):
    days_of_week = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
    timetable = {}
    if date.weekday() == 6:
        date += timedelta(days=1)
    for i in range(6 - date.weekday()):
        curr_date = (date + timedelta(days=i))
        curr_timetable = get_schedule_day(url, curr_date)
        if curr_timetable is None:
            return None
        timetable[f"{days_of_week[curr_date.weekday()]} - {curr_date.strftime('%d.%m.%y')}"] = curr_timetable
    return timetable


def compare_schedule_date(urls, date):
    # first_schedule = get_schedule_day(urls[0], date)
    # second_schedule = get_schedule_day(urls[1], date)
    #
    # [print(i, first_schedule[i]) for i in first_schedule]
    # print()
    # [print(i, second_schedule[i]) for i in second_schedule]
    #
    # print(first_schedule.keys())
    # print(second_schedule.keys())
    #
    # common_lessons = set(first_schedule.keys()).intersection(set(second_schedule.keys()))
    #
    # # for time in first_schedule:
    # #     if time in second_schedule:
    # #         common_lessons.append(time)
    #
    # return common_lessons

    # first_ics, parity = get_ics(urls[0])
    # second_ics = get_ics(urls[1])[0]
    #
    # if first_ics is not None and second_ics is not None:
    #     first_week = Calendar.from_ical(first_ics)
    #     timetable = {}
    #     for component in first_week.walk():
    #         if component.name == 'VEVENT':
    #             dt = component.get('dtstart').dt
    #             if dt.weekday() == date.weekday():
    #                 lesson_name = str(component.get('summary'))
    #                 dt_start = dt + timedelta(hours=3)
    #                 dt_end = component.get('dtend').dt + timedelta(hours=3)
    #                 duration = f"{dt_start.strftime('%H:%M')}-{dt_end.strftime('%H:%M')}"
    #                 freq = dict(component.get('rrule'))['INTERVAL'][0]
    #                 if freq == 1:
    #                     timetable[duration] = (lesson_name, str(component.get('LOCATION')))
    #                 elif freq == 2 and (date.date() - dt_start.date()).days % 2 == 0:
    #                     timetable[duration] = (lesson_name, str(component.get('LOCATION')))
    #     print(timetable)
    #     return timetable
    # return None

    first_schedule = get_schedule_day(urls[0], date)
    second_schedule = get_schedule_day(urls[1], date)
    # print(first_schedule)
    # print(second_schedule)

    if first_schedule is not None and second_schedule is not None:
        common_lessons = {
            'Общее время': [],
            'Аудитории на одном этаже': [],
            'Одинаковые аудитории': [],
        }

        for time in first_schedule:
            if time in second_schedule:
                # common_lessons[time] = (first_schedule[time][1], second_schedule[time][1])
                common_lessons['Общее время'].append((first_schedule[time][0], second_schedule[time][0]))
                if first_schedule[time][1] == second_schedule[time][1]:
                    common_lessons['Одинаковые аудитории'].append(first_schedule[time][0])
                elif first_schedule[time][1][0] == second_schedule[time][1][0] and \
                        (('л' in first_schedule[time][1] and 'л' in second_schedule[time][1]) or
                         ('ю' in first_schedule[time][1] and 'ю' in second_schedule[time][1]) or
                         ('э' in first_schedule[time][1] and 'э' in second_schedule[time][1])):
                    common_lessons['Аудитории на одном этаже'].append((first_schedule[time][0],
                                                                       second_schedule[time][0]))

        return common_lessons
    return None

    # second_week = Calendar.from_ical(second_ics)

    # парсим и сразу смотрим аудиторию и тд
