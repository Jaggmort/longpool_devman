import asyncio
import requests
import dotenv
import logging
import os
from aiogram import Bot


def main():
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
    long_poll_url = 'https://dvmn.org/api/long_polling/'
    timestamp = ''

    async def send_message(message):
        bot = Bot(token=tg_token)
        await bot.send_message(chat_id, message)
        session = await bot.get_session()
        await session.close()

    while True:
        try:
            data = {'timestamp': timestamp}
            request = requests.get(long_poll_url, headers=headers, data=data)
            request_json = request.json()
            if request_json['status'] == 'timeout':
                timestamp = request_json['timestamp_to_request']
            if request_json['status'] == 'found':
                timestamp = request_json['last_attempt_timestamp']
                if request_json['new_attempts'][0]['is_negative']:
                    reaction = 'К работе притензий нету, стоит приступать ' \
                        'к следующему заданию'
                else:
                    reaction = 'К сожалению работа требует улучшения'
                message = f'У вас проверили работу' \
                    f'\"{request_json["new_attempts"][0]["lesson_title"]}\" \n\n' \
                    f'{request_json["new_attempts"][0]["lesson_url"]} \n\n {reaction}'
                asyncio.run(send_message(message))
        except requests.exceptions.ReadTimeout:
            logging.error('ReadTimeout')
        except requests.exceptions.ConnectionError:
            logging.error('ConnectionError')


if __name__ == '__main__':
    main()
