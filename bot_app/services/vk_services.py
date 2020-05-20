import datetime
import json
import random

import pymorphy2
import vk

from bot_app import logger
from bot_app.bot_config import *
from bot_app.data.db_session import create_session
from bot_app.data.student import Student

VK_SESSION = vk.Session()
VK_API = vk.API(VK_SESSION, v=5.103)

MAILING = 'mailing'
UNSUBSCRIBE = 'Отписаться от всех рассылок'
HT_FOR_TOMORROW = 'Домашка на завтра'
MARKS_FOR_TODAY = 'Оценки за сегодня'

DATE_FORMATS = ["%Y-%m-%d", "%y-%m-%d",
                "%d.%m.%Y", "%d.%m.%y",
                "%m-%d", "%d.%m"]

WEEKDAYS = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']

MAIN_KEYBOARD = json.dumps({
    'inline': False,
    'one_time': False,
    'buttons': [
        [
            {
                'action': {
                    'type': 'text',
                    'label': HT_FOR_TOMORROW
                },
                'color': 'primary'
            },
            {
                'action': {
                    'type': 'text',
                    'label': MARKS_FOR_TODAY
                },
                'color': 'primary',
            }
        ],
        [{
            'action': {
                'type': 'text',
                'label': UNSUBSCRIBE
            },
            'color': 'negative'
        }],
        [{
            'action': {
                'type': 'text',
                'label': 'Помощь'
            },
            'color': 'positive'
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

    if new_user:
        return start(data)
    if student.dialogue_point == MAILING:
        config_mailing(vk_id, text)
    elif student.dialogue_point == 'main':
        main_point(data)


def start(data):
    message = data.get('object').get('message')
    sender = message.get('from_id')
    text = message.get('text')
    session = create_session()
    student = Student(vk_id=sender, dialogue_point='register')
    session.add(student)
    session.commit()
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


def config_mailing(vk_id, response=None):
    db_session = create_session()
    student = db_session.query(Student).filter(Student.vk_id == vk_id).first()
    if response == 'Да':
        student.daily_hometask = True
        db_session.commit()
        return end_config(vk_id)
    elif response == 'Нет':
        student.daily_hometask = False
        db_session.commit()
        return end_config(vk_id)
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
                                'хочешь получать ежедневные уведомления с домашним заданием в 16:00?'
        else:
            params['message'] = 'Просто нажми на кнопку Да/Нет'
        student.dialogue_point = 'mailing'
        db_session.commit()
        return VK_API.messages.send(**params)


def end_config(vk_id):
    db_session = create_session()
    student = db_session.query(Student).filter(Student.vk_id == vk_id).first()
    student.dialogue_point = 'main'
    params = {
        'user_id': vk_id,
        'random_id': random.randint(1, 2 ** 32),
        'message': 'Настройка завершена.',
        'keyboard': MAIN_KEYBOARD,
        'access_token': VK_APIKEY,
    }
    if student.daily_hometask:
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
        'keyboard': MAIN_KEYBOARD
    }

    if text == HT_FOR_TOMORROW:
        date = datetime.datetime.now() + datetime.timedelta(hours=16)
        hometask = school_services.get_hometask(vk_id, date)
        params['message'] = format_hometask(hometask, date)

    elif text.startswith('Домашка на') or text.startswith("Дз на"):
        date = parse_date(text.split(' ')[-1])
        if date is None:
            params['message'] = 'Сори, не могу распознать дату. Попробуй другой формат'
        else:
            hometask = school_services.get_hometask(vk_id, date)
            params['message'] = format_hometask(hometask, date)

    elif text == MARKS_FOR_TODAY:
        date = datetime.datetime.now()
        marks = school_services.get_marks(vk_id, date)
        params['message'] = format_marks(marks, date)

    elif text.startswith('Оценки за'):
        date = parse_date(text.split(' ')[-1])
        if date is None:
            params['message'] = 'Сори, не могу распознать дату. Попробуй другой формат'
        else:
            marks = school_services.get_marks(vk_id, date)
            params['message'] = format_marks(marks, date)

    elif text == 'Помощь':
        params['message'] = '''Основные команды:
"Домашка на завтра" - домашка на завтра;
"Оценки за сегодня" - оценки за сегодня;
"Домашка на <дата в формате дд.мм или дд.мм.гг>" - домашка на конкретный день;
"Оценки за <дата в формате дд.мм или дд.мм.гг>" - оценки за конкретный день;'''

    elif text == UNSUBSCRIBE:
        db_session = create_session()
        student = db_session.query(Student).filter(Student.vk_id == vk_id).first()
        student.daily_hometask = False
        db_session.commit()
        params['message'] = 'Лааадно'

    else:
        params['message'] = 'Ага'

    return VK_API.messages.send(**params)


def parse_date(datestr):
    logger.debug(f'Got datestr "{datestr}"')
    for date_format in DATE_FORMATS:
        # Перебираем различные форматы даты
        try:
            # Пробуем преобразовать дату
            date = datetime.datetime.strptime(datestr, date_format)
            date = date.replace(year=datetime.date.today().year)
            logger.debug(f'Success: {date!r}')
            # Если получилось, возвращаем ее
            return date
        except (TypeError, ValueError):
            # Иначе, пробуем другие форматы
            pass
    # И если ни один не подошел, возвращаем None
    logger.debug('Date doesn\'t match any format')
    return None


def format_hometask(hometask, date, handle_errors=True):
    formatted_date = '.'.join(str(date.date()).split('-')[::-1])
    message = ''
    if hometask is None:
        if not handle_errors:
            return None
        message = 'Произошла какая-то ошибка. Попробуй позже'
    elif type(hometask) == dict:
        morph = pymorphy2.MorphAnalyzer()
        weekday = morph.parse(WEEKDAYS[date.weekday()])[0].inflect({'accs', 'sing'}).word
        message = f'Домашка на {weekday}, {formatted_date}\n'
        for subject, task in hometask.items():
            message += f'\n • {subject}:\n{task}\n'
    elif type(hometask) == str:
        if not handle_errors:
            return None
        message = hometask
    return message


def format_marks(marks, date, handle_errors=True):
    formatted_date = '.'.join(str(date.date()).split('-')[::-1])
    message = ''
    if marks is None:
        if not handle_errors:
            return None
        message = 'Произошла какая-то ошибка. Попробуй позже'
    elif type(marks) == dict:
        morph = pymorphy2.MorphAnalyzer()
        weekday = morph.parse(WEEKDAYS[date.weekday()])[0].inflect({'accs', 'sing'}).word
        message = f'Оценки за {weekday}, {formatted_date}\n'
        for subject, marks in marks.items():
            message += f'• {subject}: {marks}\n'
    elif type(marks) == str:
        if not handle_errors:
            return None
        message = marks
    return message


def mailing_hometask():
    from bot_app.services import school_services
    db_session = create_session()
    students = db_session.query(Student).filter(Student.daily_hometask).all()
    params = {
        'access_token': VK_APIKEY,
    }

    logger.info(f'Mailing started. Number of students: {len(students)}')

    for student in students:
        student.last_mailing = datetime.datetime.now()
        date = datetime.datetime.now() + datetime.timedelta(hours=16)
        hometask = school_services.get_hometask(student.vk_id, date)
        params['user_id'] = student.vk_id
        params['random_id'] = random.randint(1, 2 ** 32)
        message = format_hometask(hometask, date, handle_errors=False)
        if message is None:
            continue
        params['message'] = message
        VK_API.messages.send(**params)

    logger.info('Mailing successful')
