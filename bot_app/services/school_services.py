import datetime

import requests
from cryptography.fernet import Fernet

from bot_app import logger
from bot_app.data.api_session import ApiSession
from bot_app.data.db_session import create_session
from bot_app.data.student import Student
from bot_app.data.subject import Subject
from bot_app.form_models.ReigsterForm import RegisterForm
from bot_app.services import vk_services
from .CRYPTO_KEYS import *


def generate_logindata(login, password):
    return Fernet(TOTAL_KEY).encrypt(Fernet(LOGIN_KEY).encrypt(login) + SEPARATOR +
                                     Fernet(PASSW_KEY).encrypt(password))


def decrypt_logindata(logindata):
    login, password = Fernet(TOTAL_KEY).decrypt(logindata).split(SEPARATOR)
    return Fernet(LOGIN_KEY).decrypt(login).decode('utf-8'), \
           Fernet(PASSW_KEY).decrypt(password).decode('utf-8')


def register(vk_id, form: RegisterForm) -> bool:
    # True, если регистрация завершена успешно, иначе - False
    db_session = create_session()
    params = {
        'login': form.login.data,
        'password': form.password.data,
    }
    r = requests.get('http://school.72to.ru/rest/login', params=params)
    response = r.json()
    if not response.get('success'):
        return False
    school_id = response['childs'][0][0]
    session_id = list(map(lambda x: x.split('='), r.headers['Set-Cookie'].split('; ')))[-3][-1]
    logindata = generate_logindata(form.login.data.encode('utf-8'),
                                   form.password.data.encode('utf-8'))
    student = db_session.query(Student).filter(Student.vk_id == vk_id).first()
    student.school_id = school_id
    student.login_data = logindata
    db_session.commit()
    api_session = ApiSession(student_id=student.id, session_id=session_id,
                             expires=datetime.datetime.now() + datetime.timedelta(hours=1))
    db_session.add(api_session)
    db_session.commit()
    vk_services.config_mailing(vk_id)
    return True


def get_hometask(vk_id, date):
    db_session = create_session()
    student = db_session.query(Student).filter(Student.vk_id == vk_id).first()
    for api_session in student.sessions:
        if api_session.expires < datetime.datetime.now():
            db_session.delete(api_session)
        else:  # Если нашли действующую сессию
            break
    else:  # И если не нашли
        api_session = create_api_session(student)
        if api_session is None:
            return None
    db_session.commit()
    headers = {'Cookie': f'sessionid={api_session.session_id}'}
    date = '.'.join(str(date.date()).split('-')[::-1])
    params = {'pupil_id': student.school_id, 'from_date': date, 'to_date': date}
    r = requests.get('http://school.72to.ru/rest/diary', params=params, headers=headers)
    response = r.json()
    try:
        lessons = response['days'][0][1]['lessons']
    except KeyError:
        return 'На выбранную дату уроков не найдено'
    ans = {}
    for lesson in lessons:
        if lesson['homework'] and lesson['homework'].lower() not in \
                ['не предусмотрено', 'не предусмотрено; не предусмотрено']:
            ans[lesson['discipline']] = lesson['homework']
        if (lesson['discipline'],) not in db_session.query(Subject.name).all():
            db_session.add(Subject(name=lesson['discipline']))
            db_session.commit()
    if ans == {}:
        return 'На выбранную дату ничего не задали. Урааа)'
    return ans


def create_api_session(student: Student):
    login, password = decrypt_logindata(student.login_data)
    params = {
        'login': login,
        'password': password,
    }
    r = requests.get('http://school.72to.ru/rest/login', params=params)
    response = r.json()
    if not response.get('success'):
        logger.error('Login failed')
        return None
    db_session = create_session()
    session_id = list(map(lambda x: x.split('='), r.headers['Set-Cookie'].split('; ')))[-3][-1]
    api_session = ApiSession(student_id=student.id, session_id=session_id,
                             expires=datetime.datetime.now() + datetime.timedelta(hours=1))
    db_session.add(api_session)
    db_session.commit()
    return api_session
