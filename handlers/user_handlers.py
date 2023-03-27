from time import sleep
from aiogram import Router, Bot
from aiogram.filters import Command, CommandStart, Text
from aiogram.types import CallbackQuery, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler


from services.vacancies import update_vacancies, check_category_link, request_new_vacansies
from services.parser import get_details
from keyboards.bottom_post_kb import create_bottom_keyboard
from database.orm import (add_vacancy_to_favorite, get_new_vacancies,
                          get_favorite_vacancies, remove_vacancy_from_favorite,
                          get_vavancy_link, add_user, get_user_id, add_category_link,
                          get_user_categories_list, clear_user_categories_list,
                          check_categories)
from lexicon.lexicon_ru import LEXICON_HELP, NO_ADDED_LINKS, NO_NEW_VACANCIES

REQUEST_INTERVAL = 60

router: Router = Router()
scheduler = AsyncIOScheduler()


@router.message(CommandStart())
async def process_start_command(message: Message):
    add_user(message.from_user.id)
    await message.answer(text='Вы запустили бот fl-bot')
    if not check_categories(message.from_user.id):
        await message.answer(text=NO_ADDED_LINKS)
    scheduler.add_job(process_request_new_vacancies_silent, 'interval', seconds=REQUEST_INTERVAL, args=(message,))
    scheduler.start()


@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_HELP, disable_web_page_preview=True)


@router.message(Command(commands='get'))
async def process_get_vacancies_command(message: Message):
    await message.answer(text='Запрашиваю новые вакансии')
    update_vacancies()


@router.message(Command(commands='request'))
async def process_request_new_vacancies_command(message: Message):
    user_id = get_user_id(message.from_user.id)
    result = request_new_vacansies(user_id)
    if isinstance(result, dict):
        for id, text in result.items():
            await message.answer(text=text, reply_markup=create_bottom_keyboard(
                        id,
                        'Подробно', '⭐️ В избранное'),
                        parse_mode='HTML')
    else:
        await message.answer(text=result)


async def process_request_new_vacancies_silent(message: Message):
    user_id = get_user_id(message.from_user.id)
    result = request_new_vacansies(user_id)
    if isinstance(result, dict):
        for id, text in result.items():
            await message.answer(text=text, reply_markup=create_bottom_keyboard(
                        id,
                        'Подробно', '⭐️ В избранное'),
                        parse_mode='HTML')


@router.message(Command(commands='favorite'))
async def process_post_favorite_vacancies_command(message: Message):
    user_id = get_user_id(message.from_user.id)
    favorite_vacancies = get_favorite_vacancies(user_id)
    if favorite_vacancies:
        await message.answer(text='Избранные вакансии:')
        for vavorite_vacancy in favorite_vacancies:
            text = (f'Вакансия № {vavorite_vacancy.id} \n'
                    f'<b>{vavorite_vacancy.title}</b> \n'
                    f'<i>{vavorite_vacancy.description}</i> \n'
                    f'{vavorite_vacancy.link}')
            await message.answer(text=text, reply_markup=create_bottom_keyboard(
                    vavorite_vacancy.id,
                    'Подробно', '❎ Из избранного'),
                    parse_mode='HTML')
    else:
        await message.answer(text='Нет избранных вакансий')


@router.callback_query(Text(startswith='⭐️ В избранное'))
async def process_add_to_favorite(callback: CallbackQuery):
    id = callback.data.split('_')[-1]
    user_id = get_user_id(callback.from_user.id)
    add_vacancy_to_favorite(user_id, id)
    await callback.answer(text='Вакансия добавлена в Избранное')
    await callback.message.edit_reply_markup(reply_markup=create_bottom_keyboard(
                    id, 'Подробно', '❎ Из избранного'))
    await callback.answer()


@router.callback_query(Text(startswith='❎ Из избранного'))
async def process_remove_from_favorite(callback: CallbackQuery):
    id = callback.data.split('_')[-1]
    user_id = get_user_id(callback.from_user.id)
    remove_vacancy_from_favorite(user_id, id)
    await callback.answer(text='Вакансия удалена из Избранного')
    await callback.message.edit_reply_markup(reply_markup=create_bottom_keyboard(
                    id, 'Подробно', '⭐️ В избранное'))
    await callback.answer()


@router.callback_query(Text(startswith='Подробно'))
async def process_details(callback: CallbackQuery):
    id = callback.data.split('_')[-1]
    link = get_vavancy_link(id)
    details = get_details(link)
    text = f'<b>Подробное описание вакансии №{id}</b> \n <i>{details}</i>'
    await callback.message.answer(text=text)


@router.message(Command(commands='addcategory'))
async def process_addlink_command(message: Message):
    await message.answer(text='Отправьте ссылку на категорию')


@router.message(Command(commands='clearcategories'))
async def process_clearlinks_command(message: Message):
    user_id = get_user_id(message.from_user.id)
    clear_user_categories_list(user_id)
    await message.answer(text='Список категорий очищен')


@router.message(Command(commands='showcategories'))
async def process_showlinks_command(message: Message):
    user_id = get_user_id(message.from_user.id)
    categories = get_user_categories_list(user_id)
    categories_list = []
    for category in categories:
        categories_list.append(str(category))
    text = '\n'.join(categories_list)
    await message.answer(text=text)


@router.message(Text(startswith='https'))
async def process_add_category_link(message: Message):
    user_id = get_user_id(message.from_user.id)
    link = message.text
    if check_category_link(link):
        if add_category_link(user_id, link):
            await message.answer(text='Категория добавлена')
    else:
        await message.answer(text='Неправильная ссылка (не соотвтетствует ссылке на RSS fl.ru)')


@router.message(Command(commands='delmenu'))
async def del_main_menu(message: Message, bot: Bot):
    await bot.delete_my_commands()
    await message.answer(text='Кнопка "Menu" удалена')
