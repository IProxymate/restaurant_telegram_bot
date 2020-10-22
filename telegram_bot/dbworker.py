import redis

from rest_bot import settings

db = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

# Пытаемся узнать из базы «состояние» пользователя
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

def save_set_of_restaurants(user_id, rest_id):
    # сохраняем id ресторанов в базу Редис
    db.sadd(f'{user_id} category', str(rest_id))

    return True

def get_set_of_restaurants(user_id):
    # Получаем множество с id ресторанов
    return db.smembers(f'{user_id} category')

def clear_set_of_restaurants(user_id):
    while (db.scard(f'{user_id} category') > 0):
        print("Removing {}...".format(db.spop(f'{user_id} category')))
    return True