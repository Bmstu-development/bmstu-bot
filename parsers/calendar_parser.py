from icalendar import Calendar
from datetime import datetime, timedelta

from parsers.web_parser import get_ics


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
                        timetable[duration] = lesson_name
                    elif freq == 2 and (date.date() - dt_start.date()).days % 2 == 0:
                        timetable[duration] = lesson_name
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
