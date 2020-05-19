import requests

from bot_app.bot_config import MAILING_KEY, SERVER_NAME

import schedule


def task():
    requests.post(f'https://{SERVER_NAME}/vk/start_mailing', json={'key': MAILING_KEY})
    print('ok')


schedule.every().day.at("16:00").do(task)

while True:
    schedule.run_pending()
