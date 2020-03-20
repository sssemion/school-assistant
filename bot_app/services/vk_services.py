import datetime
import json
import random

import pymorphy2
import vk

from bot_app.bot_config import *
from config import SERVER_NAME
from bot_app.data.db_session import create_session
from bot_app.data.student import Student

VK_SESSION = None
VK_API = None

DAILY_HOMETASK = 'daily_hometask'
MAILING_TIME = 'mailing_time'
NEW_MARKS = 'new_marks'
DEBTS_ALERTS = 'debts_alerts'

WEEKDAYS = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']

MAIN_KEYBOARD = json.dumps({
    'inline': False,
    'one_time': False,
    'buttons': [
        [{
            'action': {
                'type': 'text',
                'label': 'Домашка на завтра'
            },
            'color': 'primary'
        }],
        [
            {
                'action': {
                    'type': 'text',
                    'label': 'Оценки'
                }
            },
            {
                'action': {
                    'type': 'text',
                    'label': 'Статистика'
                }
            }
        ],
        [{
            'action': {
                'type': 'text',
                'label': 'Отписаться от всех рассылок'
            },
            'color': 'negative'
        }]
    ]
})


def handle_message(data):  # main function that receives and handle each message
    message = data.get('object').get('message')
    text = message.get('text')
    vk_id = message.get('from_id')

    db_session = create_session()
    student = db_session.query(Student).filter(Student.vk_id == vk_id).first()
    if student is None:
        new_user = True
    else:
        new_user = False

    global VK_SESSION, VK_API
    if VK_SESSION is None or VK_API is None:
        VK_SESSION = vk.Session()
        VK_API = vk.API(VK_SESSION, v=5.103)

    if new_user:
        return start(data)
    if student.dialogue_point == DAILY_HOMETASK:
        config_daily_hometask(vk_id, text)
    elif student.dialogue_point == MAILING_TIME:
        config_mailing_time(vk_id, text)
    elif student.dialogue_point == NEW_MARKS:
        config_new_marks(vk_id, text)
    elif student.dialogue_point == DEBTS_ALERTS:
        config_debts_alerts(vk_id, text)
    elif student.dialogue_point == 'main':
        main_point(data)


def start(data):
    message = data.get('object').get('message')
    sender = message.get('from_id')
    text = message.get('text')
    params = {
        'user_id': sender,
        'random_id': random.randint(1, 2 ** 32),
        'message': 'Привет! Для начала необходимо привязать свой аккаунт в электронной школе.',
        'keyboard': json.dumps({
            'inline': True,
            'buttons': [[
                {
                    'action': {
                        'type': 'open_link',
                        'link': 'https://' + SERVER_NAME + f'/register/{sender}',
                        'label': 'Регистрация'
                    }
                }
            ]]
        }),
        'access_token': VK_APIKEY,
    }
    return VK_API.messages.send(**params)


def config_daily_hometask(vk_id, response=None):
    db_session = create_session()
    student = db_session.query(Student).filter(Student.vk_id == vk_id).first()
    if response == 'Да':
        student.dialogue_point = 'daily_hometask_yes'
        student.daily_hometask = True
        db_session.commit()
        return config_mailing_time(vk_id)
    elif response == 'Нет':
        student.dialogue_point = 'daily_hometask_no'
        student.daily_hometask = False
        db_session.commit()
        return config_new_marks(vk_id)
    else:
        params = {
            'user_id': vk_id,
            'random_id': random.randint(1, 2 ** 32),
            'keyboard': json.dumps({
                'inline': False,
                'one_time': True,
                'buttons': [[
                    {
                        'action': {
                            'type': 'text',
                            'label': 'Да'
                        },
                        'color': 'positive'
                    },
                    {
                        'action': {
                            'type': 'text',
                            'label': 'Нет'
                        },
                        'color': 'negative'
                    }
                ]]
            }),
            'access_token': VK_APIKEY,
        }
        if response is None:
            params['message'] = 'Отлично! Аккаунт привязан, теперь давай займемся настройками. Ты ' \
                                'хочешь получать ежедневные уведомления с домашним заданием?'
        else:
            params['message'] = 'Просто нажми на кнопку Да/Нет'
        student.dialogue_point = DAILY_HOMETASK
        db_session.commit()
        return VK_API.messages.send(**params)


def config_mailing_time(vk_id, response=None):
    db_session = create_session()
    student = db_session.query(Student).filter(Student.vk_id == vk_id).first()
    if response:
        try:
            hh, mm = map(int, response.split(':'))
            student.mailing_time = datetime.time(hour=hh, minute=mm)
            student.dialogue_point = MAILING_TIME + '_done'
            db_session.commit()
            return config_new_marks(vk_id)
        except ValueError:
            params = {
                'user_id': vk_id,
                'random_id': random.randint(1, 2 ** 32),
                'message': 'Некорректный формат!',
                'access_token': VK_APIKEY
            }
            return VK_API.messages.send(**params)

    else:
        params = {
            'user_id': vk_id,
            'random_id': random.randint(1, 2 ** 32),
            'message': 'Тогда выбери время (в формате чч:мм), в которое хочешь получать сообщения',
            'access_token': VK_APIKEY,
        }
        student.dialogue_point = MAILING_TIME
        db_session.commit()
        return VK_API.messages.send(**params)


def config_new_marks(vk_id, response=None):
    db_session = create_session()
    student = db_session.query(Student).filter(Student.vk_id == vk_id).first()
    if response == 'Давай':
        student.dialogue_point = NEW_MARKS + '_yes'
        student.new_marks_alerts = True
    elif response == 'Не':
        student.dialogue_point = NEW_MARKS + '_no'
        student.new_marks_alerts = False
    else:
        params = {
            'user_id': vk_id,
            'random_id': random.randint(1, 2 ** 32),
            'keyboard': json.dumps({
                'inline': False,
                'one_time': True,
                'buttons': [[
                    {
                        'action': {
                            'type': 'text',
                            'label': 'Давай'
                        },
                        'color': 'positive'
                    },
                    {
                        'action': {
                            'type': 'text',
                            'label': 'Не'
                        },
                        'color': 'negative'
                    }
                ]]
            }),
            'access_token': VK_APIKEY,
        }
        if response is None:
            params['message'] = 'Идем дальше. Как насчет уведомлений о новых оценках?'
        else:
            params['message'] = 'Просто нажми на кнопку Давай/Не'
        student.dialogue_point = NEW_MARKS
        db_session.commit()
        return VK_API.messages.send(**params)
    db_session.commit()
    return config_debts_alerts(vk_id)


def config_debts_alerts(vk_id, response=None):
    db_session = create_session()
    student = db_session.query(Student).filter(Student.vk_id == vk_id).first()
    if response == 'Да':
        student.dialogue_point = DEBTS_ALERTS + '_yes'
        student.debts_alerts = True
    elif response == 'Нет':
        student.dialogue_point = DEBTS_ALERTS + '_no'
        student.debts_alerts = False
    else:
        params = {
            'user_id': vk_id,
            'random_id': random.randint(1, 2 ** 32),
            'keyboard': json.dumps({
                'inline': False,
                'one_time': True,
                'buttons': [[
                    {
                        'action': {
                            'type': 'text',
                            'label': 'Да'
                        },
                        'color': 'positive'
                    },
                    {
                        'action': {
                            'type': 'text',
                            'label': 'Нет'
                        },
                        'color': 'negative'
                    }
                ]]
            }),
            'access_token': VK_APIKEY,
        }
        if response is None:
            params['message'] = 'Последний шаг. Хочешь получать сообщения о неисправленных долгах?'
        else:
            params['message'] = 'Просто нажми на кнопку Да/Нет'
        student.dialogue_point = DEBTS_ALERTS
        db_session.commit()
        return VK_API.messages.send(**params)
    db_session.commit()
    return end_config(vk_id)


def main_point(vk_id, response=None):
    db_session = create_session()
    student = db_session.query(Student).filter(Student.vk_id == vk_id).first()
    if response is None:
        pass


def end_config(vk_id):
    db_session = create_session()
    student = db_session.query(Student).filter(Student.vk_id == vk_id).first()
    student.dialogue_point = 'main'
    params = {
        'user_id': vk_id,
        'random_id': random.randint(1, 2 ** 32),
        'message': 'Еее, настройка завершена.',
        'keyboard': MAIN_KEYBOARD,
        'access_token': VK_APIKEY,
    }
    if student.daily_hometask or student.new_marks_alerts or student.new_marks_alerts:
        params['message'] += ' Жди сообщений ;)'
    db_session.commit()
    return VK_API.messages.send(**params)


def main_point(data):
    from bot_app.services import school_services
    message = data.get('object').get('message')
    text = message.get('text')
    vk_id = message.get('from_id')
    params = {
        'user_id': vk_id,
        'random_id': random.randint(1, 2 ** 32),
        'access_token': VK_APIKEY,
    }
    if text == 'Домашка на завтра':
        date = datetime.datetime.now() + datetime.timedelta(hours=16)
        formatted_date = '.'.join(str(date.date()).split('-')[::-1])
        hometask = school_services.get_hometask(vk_id, date)
        if hometask is None:
            params['message'] = 'Произошла какая-то ошибка. Попробуйте позже'
        elif type(hometask) == dict:
            morph = pymorphy2.MorphAnalyzer()
            weekday = morph.parse(WEEKDAYS[date.weekday()])[0].inflect({'accs', 'sing'}).word
            params['message'] = f'Домашка на {weekday}, {formatted_date}\n'
            for subject, task in hometask.items():
                params['message'] += f'\n ✼ {subject}:\n{task}\n'
        elif type(hometask) == str:
            params['message'] = hometask
    else:
        params['message'] = 'Ага'
    return VK_API.messages.send(**params)
