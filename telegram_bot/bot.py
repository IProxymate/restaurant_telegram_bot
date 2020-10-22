import telebot
from django.core.paginator import Paginator
from django.db.models import Q
from telebot import types

from app.models import Restaurant, City, Category, Options
from rest_bot import settings
from telegram_bot import dbworker
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

    print(dbworker.clear_set_of_restaurants(message.from_user.id))

    cities = City.objects.all()
    cities_for_btns = {'city': [city.name for city in cities]}

    keyboard = makeKeyboard(btn_names=cities_for_btns['city'], callback_name='list_of_categories_opt')
    bot.send_message(message.chat.id, text=text, reply_markup=keyboard, parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: 'opt' in call.data)
def chosen_category(call):
    """Коллбэк хэндлер. Вызывает обработчик в зависимости от полученных данных"""

    city = get_chosen_city(call.from_user.id).decode()

    if 'Сменить город' in call.data:
        start(call.message)
    elif 'list_of_categories' in call.data:
        show_categories(call, city=None)
    elif 'Показать рестораны рядом' in call.data:
        request_users_location(call)
    elif 'Выпить' in call.data:
        drink_option(call, city)
    elif 'show_categories' in call.data:
        # удаляем из базы Редис старые id ресторанов
        dbworker.clear_set_of_restaurants(call.from_user.id)
        show_categories(call, city)
    elif 'next_page' in call.data:
        next_page_number = int(call.data[call.data.find('=') + 1:call.data.rfind('_')])

        show_option_info(call, city, next_page_number)
    elif 'previous_page' in call.data:
        previous_page_number = int(call.data[call.data.find('=') + 1:call.data.rfind('_')])
        show_option_info(call, city, previous_page_number)
    else:
        save_rests_in_redis(call, city)
        show_option_info(call, city)


def show_categories(call, city=None):
    """Вывод всех возможных категорий"""

    text = 'Отлично! Выбери подборку, куда ты хочешь сходить.'

    if city is None:
        city = call.data[0:call.data.find('_')]
        # Сохраняю город, выбранный юзверем, в БД Редис
        dbworker.save_users_city(call.from_user.id, city)

    categories = Category.objects.filter(restaurant__cities__name=city).exclude(
        Q(name__startswith='Вино') | Q(name__startswith='Коктейли') |
        Q(name__startswith='Напитки покрепче') | Q(name__startswith='Пиво')).distinct().order_by('name')

    btn_names = [category.name for category in categories]
    btn_names.append('Показать рестораны рядом')
    btn_names.append('Сменить город')

    keyboard = makeKeyboard(btn_names, callback_name='opt', row_width=1)

    bot.edit_message_text(chat_id=call.message.chat.id,
                          text=text,
                          message_id=call.message.message_id,
                          reply_markup=keyboard,
                          parse_mode='HTML')


def save_rests_in_redis(call, city):
    # получаем QuerySet со всеми ресторанами нужной категории
    chosen_cat = call.data[0:-4]
    restaurants_list = Restaurant.objects.filter(cities__name__contains=city).filter(
        categories__name=chosen_cat).order_by('id').iterator()

    for restaurant in restaurants_list:
        dbworker.save_set_of_restaurants(call.from_user.id, restaurant.id)


def drink_option(call, city):
    """Обработчик категории 'Выпить'. Отображает подкатегории """

    text = 'Что хочешь выпить?'

    drink_options = Category.objects.filter(
        Q(restaurant__cities__name__startswith=city) & Q(name__startswith='Вино') | Q(
            name__startswith='Коктейли') | Q(name__startswith='Напитки покрепче') | Q(
            name__startswith='Пиво')).distinct().order_by('name')

    btn_names = [option.name for option in drink_options]

    keyboard = makeKeyboard(btn_names, callback_name='opt', row_width=1)
    # TODO ебалу делаю, потом поменять все надо))
    keyboard.add(types.InlineKeyboardButton(text='Сменить город', callback_data='Сменить город_opt'))

    bot.edit_message_text(chat_id=call.message.chat.id,
                          text=text,
                          message_id=call.message.message_id,
                          reply_markup=keyboard,
                          parse_mode='HTML')


def show_option_info(call, city, page_number=None):
    """Постранично отображаем информацию о ресторанах выбранной категории"""

    restaurant_ids = dbworker.get_set_of_restaurants(call.from_user.id)
    list_of_restaurant_ids = [int(id) for id in restaurant_ids]

    items_on_page = 5

    paginator = Paginator(list_of_restaurant_ids, items_on_page)
    if page_number is None:
        page_number = 1
        page = paginator.get_page(page_number)
        print(page.object_list)
    else:
        page = paginator.get_page(page_number)

    restaurant_options = Options.objects.all()

    text = f'''<b>Кофе в {city} ({page_number}/{paginator.num_pages})</b>\n\n<b>Условные обозначения:</b>'''

    for i in restaurant_options:
        text += f'\n<i>{i.name}</i>'

    text += get_text(page)
    keyboard = get_keyboard(page)

    bot.edit_message_text(chat_id=call.message.chat.id,
                          text=text,
                          message_id=call.message.message_id,
                          reply_markup=keyboard,
                          parse_mode='HTML')


def get_text(page):
    page_content = Restaurant.objects.filter(id__in=page.object_list).order_by('name')
    text = ''

    for i in page_content:
        text += f'''\n\n<b>{i.name}</b>\n{i.short_description}\n<a href="{i.google_map_link}">{i.address}</a>'''
    return text


def get_keyboard(page):
    keyboard = types.InlineKeyboardMarkup(row_width=5)
    if page.has_next() and page.has_previous():
        keyboard.add(
            types.InlineKeyboardButton(text='Хочу еще >', callback_data=f'next_page={page.next_page_number()}_opt'))
        keyboard.add(types.InlineKeyboardButton(text='< Назад',
                                                callback_data=f'previous_page={page.previous_page_number()}_opt'))
        keyboard.add(types.InlineKeyboardButton(text='<<< Вернуться к подборкам', callback_data='show_categories_opt'))
        return keyboard
    elif page.has_next():
        keyboard.add(
            types.InlineKeyboardButton(text='Хочу еще >', callback_data=f'next_page={page.next_page_number()}_opt'))
        keyboard.add(types.InlineKeyboardButton(text='<<< Вернуться к подборкам', callback_data='show_categories_opt'))
        return keyboard
    else:
        keyboard.add(types.InlineKeyboardButton(text='< Назад',
                                                callback_data=f'previous_page={page.previous_page_number()}_opt'))
        keyboard.add(types.InlineKeyboardButton(text='<<< Вернуться к подборкам', callback_data='show_categories_opt'))
        return keyboard


# Работа с геопозицией юзера
def request_users_location(call):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
    keyboard.add(button_geo)
    bot.send_message(call.message.chat.id,
                     "Поделитесь своим местоположением!",
                     reply_markup=keyboard)


@bot.message_handler(content_types=['location'])
def test(message):
    user_location_longitude = message.location.longitude
    user_location_latitude = message.location.latitude
    print(user_location_longitude, user_location_latitude)


# Вебхук бота
bot.remove_webhook()
bot.set_webhook(url=f"{settings.DOMAIN}/{settings.BOT_TOKEN}")
