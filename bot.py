import asyncio
import requests
import dotenv
import logging
import os
from aiogram import Bot


dotenv.load_dotenv('.env')
tg_token = os.environ['TELEGRAM_TOKEN']
dvmn_token = os.environ['DEVMAN_TOKEN']
chat_id = int(os.environ['CHAT_ID'])
headers = {'Authorization': dvmn_token}
logging.basicConfig(
    filename='events.log',
    encoding='utf-8',
    level=logging.DEBUG
    )
url2 = 'https://dvmn.org/api/long_polling/'
timestamp = ''


async def send_message(message):
    bot = Bot(token=tg_token)
    await bot.send_message(chat_id, message)
    session = await bot.get_session()
    await session.close()


while True:
    try:
        data = {'timestamp': timestamp}
        rs = requests.get(url2, headers=headers, data=data)
        r = rs.json()
        if r['status'] == 'timeout':
            timestamp = r['timestamp_to_request']
        if r['status'] == 'found':
            timestamp = r['last_attempt_timestamp']
            if r['new_attempts'][0]['is_negative']:
                reaction = 'К работе притензий нету, стоит приступать ' \
                    'к следующему заданию'
            else:
                reaction = 'К сожалению работа требует улучшения'
            message = f'У вас проверили работу' \
                f'\"{r["new_attempts"][0]["lesson_title"]}\" \n\n' \
                f'{r["new_attempts"][0]["lesson_url"]} \n\n {reaction}'
            asyncio.run(send_message(message))
    except requests.exceptions.ReadTimeout:
        logging.error('ReadTimeout')
    except requests.exceptions.ConnectionError:
        logging.error('ConnectionError')
