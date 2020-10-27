import redis

from app.models import Restaurant
from rest_bot import settings

db = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


def get_chosen_city(user_id):
    try:
        return db[user_id]
    except KeyError:  # Если такого ключа почему-то не оказалось
        return 'You have to choose city'  # значение по умолчанию - начало диалога


# Сохраняем текущее «состояние» пользователя в нашу базу
def save_users_city(user_id, city):
    try:
        db[user_id] = city
        return True
    except:
        # тут желательно как-то обработать ситуацию
        return False


def save_set_of_restaurants(user_id, rest_id, distance):
    # сохраняем id ресторанов в базу Редис
    # db.sadd(f'{user_id} category', str(rest_id))
    rest_info = {f'{rest_id}': f'{distance}'}
    db.hmset(f'{user_id} category', rest_info)
    return True


def get_set_of_restaurants(user_id):
    # Получаем множество с id ресторанов
    return db.hgetall(f'{user_id} category')


def clear_set_of_restaurants(user_id):
    try:
        all_keys = list(db.hgetall(f'{user_id} category').keys())
        db.hdel(f'{user_id} category', *all_keys)
    except redis.exceptions.ResponseError:
        pass
    return True


def save_user_location(user_id, longitude, latitude):
    location = {'longitude': f'{longitude}', 'latitude': f'{latitude}'}
    db.hmset(f'{user_id} location', location)


def get_user_location(user_id):
    location = db.hgetall(f'{user_id} location')
    return location

def get_distance_of_rest(user_id, rest_id):
    distance = db.hget(f'{user_id} category', rest_id)
    return distance.decode()
