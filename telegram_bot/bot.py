import telebot
from django.core.paginator import Paginator
from django.db.models import Q
from telebot import types

from app.models import City, Category, Restaurant
from rest_bot import settings
from telegram_bot import dbworker, config
from telegram_bot.dbworker import get_chosen_city

bot = telebot.TeleBot(settings.BOT_TOKEN)


def makeKeyboard(btn_names, callback_name=None, row_width=2):
    keyboard = types.InlineKeyboardMarkup(row_width=row_width)

    keyboard.add(
        *[types.InlineKeyboardButton(text=name, callback_data=f'{name}_{callback_name}') for name in btn_names])
    return keyboard


@bot.message_handler(commands=['start'])
def start(message):
    text = 'Привет!🤗\nЯ помогу тебе выбрать ресторан.\nВ каком городе ищем?'

    cities = City.objects.all()
    cities_for_btns = {'city': [city.name for city in cities]}

    keyboard = makeKeyboard(btn_names=cities_for_btns['city'], callback_name='list_of_categories')
    bot.send_message(message.chat.id, text=text, reply_markup=keyboard, parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: 'list_of_categories' in call.data)
def show_categories(call):
    """Вывод всех возможных категорий"""

    text = 'Отлично! Выбери подборку, куда ты хочешь сходить.'

    city = call.data[0:call.data.find('_')]
    # Сохраняю город, выбранный юзверем, в БД Редис
    dbworker.save_users_city(call.message.from_user.id, city)

    categories = Category.objects.filter(restaurant__cities__name=city).exclude(
        Q(name__startswith='Вино') | Q(name__startswith='Коктейли') |
        Q(name__startswith='Напитки покрепче') | Q(name__startswith='Пиво')).distinct()

    btn_names = [category.name for category in categories]
    btn_names.append('Показать рестораны рядом')
    btn_names.append('Сменить город')

    keyboard = makeKeyboard(btn_names, callback_name='opt', row_width=1)

    bot.edit_message_text(chat_id=call.message.chat.id,
                          text=text,
                          message_id=call.message.message_id,
                          reply_markup=keyboard,
                          parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: 'opt' in call.data)
def chosen_category(call):
    """Коллбэк хэндлер. Вызывает обработчик в зависимости от полученных данных"""

    if 'Сменить город' in call.data:
        start(call.message)
    elif 'Показать рестораны рядом' in call.data:
        print('Потом доделаем. Переход к команде /nearme{{city}}')
    elif 'Выпить' in call.data:
        chosen_cat = call.data[0:call.data.rfind(' ')]
        drink_option(call, chosen_cat)
    else:
        show_option_info(call)


def drink_option(call, chosen_cat):
    """Обработчик категории 'Выпить'. Отображает подкатегории """

    text = 'Что хочешь выпить?'

    # Получаем выбранный ранее город юзера
    city = get_chosen_city(call.message.from_user.id).decode()

    drink_options = Category.objects.filter(
        Q(restaurant__cities__name__startswith=city) & Q(name__startswith='Вино') | Q(
            name__startswith='Коктейли') | Q(name__startswith='Напитки покрепче') | Q(
            name__startswith='Пиво')).distinct()

    btn_names = [option.name for option in drink_options]

    keyboard = makeKeyboard(btn_names, callback_name='opt', row_width=1)
    # TODO ебалу делаю, потом поменять все надо))
    keyboard.add(types.InlineKeyboardButton(text='Сменить город', callback_data='Сменить город_opt'))

    bot.edit_message_text(chat_id=call.message.chat.id,
                          text=text,
                          message_id=call.message.message_id,
                          reply_markup=keyboard,
                          parse_mode='HTML')


def show_option_info(call):
    chosen_cat = call.data[0:-4]
    # Получаем выбранный ранее город юзера
    city = get_chosen_city(call.message.from_user.id).decode()

    restaurants_list = Restaurant.objects.filter(cities__name__contains=city).filter(
        categories__name=chosen_cat).order_by('id')

    text = f'''<b>Кофе в {city} (1/6)</b>

    <b>Условные обозначения:</b>
    🐶 <i>dog-friendly</i>
    🍴 <i>есть завтраки</i>
    🌿 <i>есть веранда/терраса</i>
'''
    for i in restaurants_list:
        text += f'''\n\n<b>{i.name}</b>
{i.short_description}
<a href="{i.google_map_link}">{i.address}</a>'''



    bot.edit_message_text(chat_id=call.message.chat.id,
                          text=text,
                          message_id=call.message.message_id,
                          parse_mode='HTML')


# Вебхук бота
bot.remove_webhook()
bot.set_webhook(url=f"{settings.DOMAIN}/{settings.BOT_TOKEN}")
