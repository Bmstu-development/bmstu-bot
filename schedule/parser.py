import requests
from bs4 import BeautifulSoup
from schedule.edit_strings import *
import re

URL = 'https://lks.bmstu.ru/schedule/list'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
           'accept': '*/*'}


# def get_html(url, params=None):
#     return requests.get(url, headers=HEADERS, params=params)
#
#
# html = get_html(URL)
#
#
# def get_link(group):
#     if html.status_code == 200:
#         soup = BeautifulSoup(html.text, 'html.parser')
#         nested_items = soup.find_all('div', class_='accordion')
#         for nested_item in nested_items:
#             if edit_strings.normalize(nested_item.get_text()).find(edit_strings.find_faculty(group)) == 1 and \
#                     group in edit_strings.normalize(nested_item.get_text()):
#                 for item in nested_item.find_all('a'):
#                     if group in edit_strings.normalize(item.get_text()):
#                         return URL[:URL.find('ru') + 2] + item.attrs['href']
#     else:
#         print('Error: html code is %code' % html.status_code)
#
#
# def get_faculties():
#     groups = []
#     if html.status_code == 200:
#         soup = BeautifulSoup(html.text, 'html.parser')
#         items = soup.find_all('a', class_='list-group-item')
#         for item in items:
#             content = item.get_text()
#             groups.append(edit_strings.clean_string(content))
#     else:
#         groups = ['Error: html code is %code' % html.status_code]
#     return groups
#
#
# def get_groups(faculty, drop_invalid=True):
#     lt = []
#     if html.status_code == 200:
#         soup = BeautifulSoup(html.text, 'html.parser')
#         items = soup.find_all('div', class_='accordion')
#         for item in items:
#             lt.append(edit_strings.clean_string(item.get_text()))
#         lt = [i for i in lt if faculty == edit_strings.find_faculty(i)]
#     else:
#         print('Error: html code is %code' % html.status_code)
#     return lt


# def get_schedule(group):
#     html = requests.get(URL, headers=HEADERS)
#     if html.status_code == 200:
#         soup = BeautifulSoup(html.text, 'html.parser')
#         nested_items = soup.find_all('div', class_='accordion')
#         for nested_item in nested_items:
#             if normalize(nested_item.get_text()) in group:
#                 for item in nested_item.find_all('a'):
#                     if group in normalize(item.get_text()):
#                         return URL[:URL.find('ru') + 2] + item.attrs['href']
#     else:
#         print('Error: html code is %code' % html.status_code)


def normalize(s):
    s = s.replace('\n', ' ')
    while s.find('  ') != -1:
        s = s.replace('  ', ' ')
    return s


def get_schedule(group_id):
    if not re.match(r'^[А-Я]{1,4}[0-9]{1,2}-[0-9]{2,3}[БАМ]?$', group_id):
        return 'Wrong format of group. Should be like ИБМ6-12Б or Э4-33'
    resp = requests.get(URL, headers=HEADERS)
    if resp.ok:
        soup = BeautifulSoup(resp.text, 'html.parser')
        nested_items = soup.find_all('div', class_='accordion')
        for nested_item in nested_items:
            if group_id in normalize(nested_item.get_text()):
                for item in nested_item.find_all('a'):
                    if group_id in normalize(item.get_text()):
                        return URL[:URL.find('ru') + 2] + item.attrs['href']
        return 'Group was not found'
    return 'Something went wrong, try again later'
