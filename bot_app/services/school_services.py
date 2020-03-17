import requests
from cryptography.fernet import Fernet

from data.db_session import create_session
from data.student import Student
from form_models.ReigsterForm import RegisterForm
from services import vk_services
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
    params = {
        'login': form.login.data,
        'password': form.password.data,
    }
    r = requests.get('http://school.72to.ru/rest/login', params=params)
    response = r.json()
    if not response.get('success'):
        return False
    logindata = generate_logindata(form.login.data.encode('utf-8'),
                                   form.password.data.encode('utf-8'))
    db_session = create_session()
    student = Student(vk_id=vk_id, login_data=logindata, dialogue_point='register')
    db_session.add(student)
    db_session.commit()
    vk_services.config_daily_hometask(vk_id)
    return True
