from aiogram import Router, Bot
from aiogram.filters import Command, CommandStart, Text
from aiogram.types import CallbackQuery, Message

from services.vacancies import update_vacancies
from services.parser import get_details
from keyboards.bottom_post_kb import create_bottom_keyboard
from database.orm import (add_vacancy_to_favorite, get_new_vacancies,
                          get_favorite_vacancies, remove_vacancy_from_favorite,
                          get_vavancy_link, add_user, get_user_id, add_category_link,
                          get_user_categories_list)

router: Router = Router()


@router.message(CommandStart())
async def process_start_command(message: Message):
    add_user(message.from_user.id)
    await message.answer(text='Вы запустили бот fl-bot')


@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text='Бот мониторит вакансии на fl.ru по заданным категориям'
                         'и показывает новые с возможностью перейти по ссылке в вакансию')


@router.message(Command(commands='get'))
async def process_get_vacancies_command(message: Message):
    await message.answer(text='Запрашиваю новые вакансии')
    update_vacancies()


@router.message(Command(commands='request'))
async def process_post_new_vacancies_command(message: Message):
    user_id = get_user_id(message.from_user.id)
    categories = get_user_categories_list(user_id)
    if categories:
        update_vacancies(user_id, categories)
        new_vacancies = get_new_vacancies()
        if new_vacancies:
            await message.answer(text='Список новых вакансий:')
            for new_vacancy in new_vacancies:
                text = (f'Вакансия № {new_vacancy.id} \n'
                        f'<b>{new_vacancy.title}</b> \n'
                        f'<i>{new_vacancy.description}</i> \n'
                        f'{new_vacancy.link}')
                await message.answer(text=text, reply_markup=create_bottom_keyboard(
                        new_vacancy.id,
                        'Подробно', '⭐️ В избранное'),
                        parse_mode='HTML')
        else:
            await message.answer(text='Новых вакансий пока нет')
    else:
        await message.answer(text='У вас не добавлено ни одно категории, для добавление используйте команду /addlink')


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


@router.message(Command(commands='addlink'))
async def process_addlink_command(message: Message):
    await message.answer(text='Отправьте ссылку на категорию')


@router.message(Text(startswith='https'))
async def process_add_category_link(message: Message):
    user_id = get_user_id(message.from_user.id)
    link = message.text
    print(f'===== Passing user_id:{user_id} and link:{link}')
    if add_category_link(user_id, link):
        await message.answer(text='Категория добавлена')


@router.message(Command(commands='delmenu'))
async def del_main_menu(message: Message, bot: Bot):
    await bot.delete_my_commands()
    await message.answer(text='Кнопка "Menu" удалена')