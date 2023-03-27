import requests

from bs4 import BeautifulSoup
from fake_useragent import UserAgent


def get_data(url):
    ua = UserAgent()
    fake_headers = {'user-agent': ua.random.strip()}

    session = requests.Session()
    session.headers.update(fake_headers)

    try:
        response = session.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
    except Exception as error:
        print('Возникла ошибка парсинга в get_data: ', error)
        soup = None
    return soup


def get_details(url):
    soup = get_data(url)
    try:
        details = soup.find('div', {'class': 'text-5 b-layout__txt_padbot_20'}).text
        return details
    except Exception as error:
        print('Возникла ошибка парсинга в get_details: ', error)
        return 'Не удалось получить подробное описание'

