import requests
from bs4 import BeautifulSoup
import re

from config import URL, HEADERS


def normalize(s):
    s = s.replace('\n', ' ')
    while s.find('  ') != -1:
        s = s.replace('  ', ' ')
    return s


def get_link(group_id):
    if not re.match(r'^[А-Я]{1,4}[0-9]{1,2}-[0-9]{2,3}[БАМ]?$', group_id):
        return False, 'Неверный формат номера группы. Должно быть, например, ИБМ6-12Б или Э4-33 и тп'
    resp = requests.get(URL, headers=HEADERS)
    if resp.ok:
        soup = BeautifulSoup(resp.text, 'html.parser')
        nested_items = soup.find_all('div', class_='accordion')
        for nested_item in nested_items:
            if group_id in normalize(nested_item.get_text()):
                for item in nested_item.find_all('a'):
                    if group_id == normalize(item.get_text()).replace(' ', ''):
                        return True, URL[:URL.find('ru') + 2] + item.attrs['href']
        return False, 'Группа не найдена!'
    return False, 'Что-то пошло не так, попробуйте позже!'


def get_link_ics(link):
    pass


def get_ics(url):
    resp = requests.get(url, headers=HEADERS)
    ics = None
    parity = None
    if resp.ok:
        soup = BeautifulSoup(resp.text, 'html.parser')
        links = soup.find_all('div', class_='col-md-8')
        for fields in links:
            # link for ics file
            for href in fields.find_all('a'):
                if '.ics' in href.attrs['href']:
                    ics = requests.get(URL[:URL.find('ru') + 2] + href.attrs['href'], headers=HEADERS).content
            # header
            header_text = fields.find('i').get_text()
            if 'числитель' in header_text:
                parity = False
            elif 'знаменатель' in header_text:
                parity = True
    return ics, parity
