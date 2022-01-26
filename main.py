import vk_api
from vk_api import VkUpload
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import threading
import random
import pymysql
import pymysql.cursors
import requests


def get_connection():
    connection = pymysql.connect(host="%name_host%",
                                 user="%name_user%",
                                 password="%password_user%",
                                 db="vktest",
                                 charset="utf8mb4",
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection


def send_message(id_user, id_keyboard, message_text):
    try:
        vk.messages.send(
             user_id=id_user,
             random_id=get_random_id(),
             keyboard=open(id_keyboard, 'r', encoding='UTF-8').read(),
             message=message_text)
    except:
        print("Ошибка отправки сообщения у id" + id_user)


def add_new_line(id_user):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO user (iduser, position) VALUES (%s, %s)"
            cursor.execute(sql, (id_user, "1"))
        connection.commit()
    finally:
        connection.close()
    return


def take_position(id_user):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT position FROM user WHERE iduser = %s"
            cursor.execute(sql, (id_user))
            line = cursor.fetchone()
            if line is None:
                return_count = 0
            else:
                return_count = line["position"]
    finally:
        connection.close()
    return return_count


def update_position(id_user, new_position):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE user SET position = %s WHERE iduser = %s"
            cursor.execute(sql, (new_position, id_user))
        connection.commit()
    finally:
        connection.close()
    return


def durov_quote():
    durov = ['Лучшее решение из возможных — самое простое. И наоборот.',
             'Что такое университет? Это же раздробленная структура с удельными княжествами.',
             'Коммуникация переоценена. Час одиночества продуктивнее недели разговоров.',
             'Проблемы — это спрятанные решения.',
             'Врать вредно для духовной целостности.']
    return random.choice(durov)


def zuckerberg_quote():
    zuckerberg = ['В мире, который меняется очень быстро, единственная стратегия, которая гарантированно '
                  'провальна — не рисковать.',
                  'Двигайтесь быстро и разрушайте препятствия. Если вы ничего не разрушаете, '
                  'Вы движетесь недостаточно быстро.',
                  'Вопрос не в том, что мы хотим знать о человеке. Вопрос стоит так:'
                  '«Что люди хотят рассказать о себе?»',
                  'Люди могут быть очень умными или иметь отличные профессиональные навыки, '
                  'но если они действительно не верят в свое дело, они не будут по-настоящему работать.',
                  'Вопрос, который я задаю себе почти каждый день: сделал ли я самую важную вещь, которую '
                  'я мог бы сделать? Если я не чувствую, что я работаю над самой важной проблемой, где я '
                  'могу помочь, я не буду чувствовать, что хорошо провожу свое время']
    return random.choice(zuckerberg)


def processing_message(id_user, message_text):
    number_position = take_position(id_user)

    if number_position == 0:
        send_message(id_user, "keyboard_main.json", "Тебя приветствует бот!")
        add_new_line(id_user)

    elif number_position == 1:
        if message_text == "Цитаты Дурова":
            update_position(id_user, "2")
            send_message(id_user, "keyboard_durov.json", durov_quote())
        elif message_text == "Цитаты Цукерберга":
            update_position(id_user, "3")
            send_message(id_user, "keyboard_zuckerberg.json", zuckerberg_quote())
        else:
            send_message(id_user, "keyboard_main.json", "Непонятная команда")

    elif number_position == 2:
        if message_text == "Хочу ещё Дурова":
            send_message(id_user, "keyboard_durov.json", durov_quote())
        elif message_text == "Выйти в главное меню":
            update_position(id_user, "1")
            send_message(id_user, "keyboard_main.json", "Мы в главном меню")
        else:
            send_message(id_user, "keyboard_durov.json", "Непонятная команда")

    elif number_position == 3:
        if message_text == "Хочу ещё Цукерберга":
            send_message(id_user, "keyboard_zuckerberg.json", zuckerberg_quote())
        elif message_text == "Выйти в главное меню":
            update_position(id_user, "1")
            send_message(id_user, "keyboard_main.json", "Мы в главном меню")
        else:
            send_message(id_user, "keyboard_zuckerberg.json", "Непонятная команда")
    else:
        send_message(id_user, "keyboard_main.json", "Произошла какая-то ошибка")


if __name__ == '__main__':
    while True:
        session = requests.Session()
        vk_session = vk_api.VkApi(token="%Токен сообщества VK%")
        vk = vk_session.get_api()
        upload = VkUpload(vk_session)
        longpoll = VkBotLongPoll(vk_session, "%ID сообщества VK%")
        try:
            for event in longpoll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW and event.from_user:
                    threading.Thread(target=processing_message, args=(event.obj.from_id, event.obj.text)).start()
        except Exception:
            pass
