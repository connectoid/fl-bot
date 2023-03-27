from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from .models import Base, Vacancy, User, CategoryLink
from config_data.config import load_config, Config

config: Config = load_config()

database_url = f'postgresql://postgres:postgres@{config.db.db_host}:5432/{config.db.database}'

engine = create_engine(database_url, echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def add_user(tg_id):
    session = Session()
    user = session.query(User).filter(User.tg_id == tg_id).first()
    if user is None:
        new_user = User(tg_id=tg_id)
        session.add(new_user)
        session.commit()


def get_user_id(tg_id):
    session = Session()
    user = session.query(User).filter(User.tg_id == tg_id).first()
    return user.id


def add_vacancy(user_id, title, description, link):
    session = Session()
    vacancy = session.query(Vacancy).filter(Vacancy.title == title, Vacancy.owner == user_id).first()
    if vacancy is None:
        new_vacancy = Vacancy(title=title, description=description, link=link, owner=user_id)
        session.add(new_vacancy)
        session.commit()


def set_vacancy_reviewed(user_id, id):
    session = Session()
    vacancy = session.query(Vacancy).filter(Vacancy.id == id, Vacancy.owner == user_id).first()
    vacancy.is_new = False
    session.add(vacancy)
    session.commit()


def add_vacancy_to_favorite(user_id, id):
    session = Session()
    vacancy = session.query(Vacancy).filter(Vacancy.id == id, Vacancy.owner == user_id).first()
    vacancy.is_favorite = True
    session.add(vacancy)
    session.commit()


def remove_vacancy_from_favorite(user_id, id):
    session = Session()
    vacancy = session.query(Vacancy).filter(Vacancy.id == id, Vacancy.owner == user_id).first()
    vacancy.is_favorite = False
    session.add(vacancy)
    session.commit()


def get_new_vacancies():
    session = Session()
    vacancies = session.query(Vacancy).filter(Vacancy.is_new == True).all()
    for vacancy in vacancies:
        set_vacancy_reviewed(vacancy.owner, vacancy.id)
    return vacancies


def get_favorite_vacancies(user_id):
    session = Session()
    vacancies = session.query(Vacancy).filter(Vacancy.is_favorite == True, Vacancy.owner == user_id).all()
    return vacancies


def get_vavancy_link(id):
    session = Session()
    vacancy = session.query(Vacancy).filter(Vacancy.id == id).first()
    return vacancy.link


def add_category_link(user_id, link) -> bool:
    session = Session()
    existing_link = session.query(CategoryLink).filter(CategoryLink.owner == user_id, CategoryLink.link == link).first()
    if existing_link is None:
        new_link = CategoryLink(link=link, owner=user_id)
        session.add(new_link)
        session.commit()
        return True
    return False


def clear_user_categories_list(user_id):
    session = Session()
    session.query(CategoryLink).filter(CategoryLink.owner == user_id).delete()
    session.commit()


def get_user_categories_list(user_id):
    session = Session()
    categories_list = session.query(CategoryLink).filter(CategoryLink.owner == user_id).all()
    return categories_list


def check_categories(user_id):
    session = Session()
    if session.query(CategoryLink).filter(CategoryLink.owner == user_id).first():
        return True
    return False


def enable_auto(user_id):
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()
    user.is_scheduled = True
    session.commit()


def disable_auto(user_id):
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()
    user.is_scheduled = False
    session.commit()


def is_auto_enabled(user_id):
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()
    if user.is_scheduled:
        return True
    return False