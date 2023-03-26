from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from .models import Base, Vacancy, User, CategoryLink
#from settings.database_config import database_url
 
#engine = create_engine(database_url, echo=True)
engine = create_engine('postgresql://postgres:postgres@localhost:5432/flbotdb', echo=False)
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
    print('============ passing vacancy:', title)
    if vacancy is None:
        print('============ add to db vacancy:', title)
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
        print(vacancy.id)
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
        print('**************** Link is None')
        print('============ add to db link:', link)
        new_link = CategoryLink(link=link, owner=user_id)
        session.add(new_link)
        session.commit()
        return True
    return False


def get_user_categories_list(user_id):
    session = Session()
    categories_list = session.query(CategoryLink).filter(CategoryLink.owner == user_id).all()
    print('^^^^^^^^^^^^^^^^', categories_list)
    return categories_list