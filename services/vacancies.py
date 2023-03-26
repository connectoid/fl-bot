import requests

from rss_parser import Parser
from fake_useragent import UserAgent

from database.orm import (add_vacancy, get_new_vacancies,
                          set_vacancy_reviewed, add_vacancy_to_favorite,
                          )


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
        print('============ found vacancy:', title)
        add_vacancy(user_id, title, description, link)


def update_vacancies(user_id, categories):
    for category in categories:
        print('######### requesting fo category:', category)
        get_vacancies(user_id, category)

