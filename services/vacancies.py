import requests
import re

from rss_parser import Parser
from fake_useragent import UserAgent

from database.orm import (add_vacancy, get_new_vacancies,
                          set_vacancy_reviewed, add_vacancy_to_favorite,
                          get_user_categories_list
                          )
from lexicon.lexicon_ru import NO_ADDED_LINKS, NO_NEW_VACANCIES

rss_url = 'https://www.fl.ru/rss/all.xml?subcategory=37&category=5p'

categories_test = [
    'https://www.fl.ru/rss/all.xml?subcategory=279&category=5', # Программирование, разработка чат-ботов
    'https://www.fl.ru/rss/all.xml?subcategory=280&category=5', # Программирование, парсинг данных
    'https://www.fl.ru/rss/all.xml?subcategory=37&category=5', # Программирование, веб-программировние
]


def get_feed(url):
    ua = UserAgent()
    fake_headers = {'user-agent': ua.random.strip()}

    session = requests.Session()
    session.headers.update(fake_headers)
    xml = session.get(url)
    parser = Parser(xml=xml.content, limit=5)
    feed = parser.parse()
    return feed


def get_vacancies(user_id, category):
    feed = get_feed(category)
    for item in feed.feed:
        title = item.title
        description = item.description
        link = item.link
        add_vacancy(user_id, title, description, link)


def update_vacancies(user_id, categories):
    for category in categories:
        get_vacancies(user_id, category)


def request_new_vacansies(user_id):
    categories = get_user_categories_list(user_id)
    new_vacancies_dict = {}
    if categories:
        update_vacancies(user_id, categories)
        new_vacancies = get_new_vacancies()
        if new_vacancies:
            for new_vacancy in new_vacancies:
                text = (f'Вакансия № {new_vacancy.id} \n'
                        f'<b>{new_vacancy.title}</b> \n'
                        f'<i>{new_vacancy.description}</i> \n'
                        f'{new_vacancy.link}')
                new_vacancies_dict[new_vacancy.id] = text
            return new_vacancies_dict
        else:
            return NO_NEW_VACANCIES
    else:
        return NO_ADDED_LINKS


def check_category_link(link: str) -> bool:
    pattern = re.compile(r'https://www.fl.ru/rss/all.xml\?subcategory=[0-9]+&category=[0-9]+')
    result = pattern.match(link)
    if result:
        return True
    return False
