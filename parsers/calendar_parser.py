from icalendar import Calendar
from datetime import datetime, timedelta

from parsers.web_parser import get_ics


def get_schedule_today(url):
    ics_string, parity = get_ics(url)
    if ics_string is not None:
        week = Calendar.from_ical(ics_string)
        timetable = {}
        for component in week.walk():
            if component.name == "VEVENT":
                dt = component.get('dtstart').dt
                if dt.weekday() == datetime.now().weekday():
                    # if dict(component.get('rrule'))['INTERVAL'][0] == 2:
                    #     if is_today(component):
                    #         timetable[duration] = str(component.get('summary'))
                    # else:
                    #     timetable[duration] = str(component.get('summary'))

                    # if duration in timetable:
                    #     if parity:
                    #         timetable[duration] = str(component.get('summary'))
                    #         parity = not parity
                    # else:
                    #     timetable[duration] = str(component.get('summary'))
                    #     parity = not parity

                    # print(str(component.get('summary')), dt_start, dt_end, dict(component.get('rrule'))['INTERVAL'][0])
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
                                dt_end = dt_start + timedelta(minutes=95)
                                break
                    else:
                        dt_start = dt + timedelta(hours=3)
                        dt_end = component.get('dtend').dt + timedelta(hours=3)
                    duration = f"{dt_start.strftime('%H:%M')}-{dt_end.strftime('%H:%M')}"
                    freq = dict(component.get('rrule'))['INTERVAL'][0]
                    if freq == 1:
                        timetable[duration] = lesson_name
                    elif freq == 2 and (datetime.now().date() - dt_start.date()).days % 2 == 0:
                        timetable[duration] = lesson_name

                    # if duration in timetable:
                    #     if parity:
                    #         timetable[duration] = str(component.get('summary'))
                    # else:
                    #     timetable[duration] = str(component.get('summary'))
        return timetable
    return None
