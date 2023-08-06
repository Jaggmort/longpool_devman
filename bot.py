import asyncio
import requests
import dotenv
import logging
import os
from aiogram import Bot
from textwrap import dedent


async def main():
    dotenv.load_dotenv('.env')
    tg_token = os.environ['TELEGRAM_TOKEN']
    dvmn_token = os.environ['DEVMAN_TOKEN']
    chat_id = int(os.environ['TELEGRAM_CHAT_ID'])
    headers = {'Authorization': dvmn_token}
    bot = Bot(token=tg_token)
    logging.basicConfig(
        filename='events.log',
        encoding='utf-8',
        level=logging.DEBUG
        )
    long_poll_url = 'https://dvmn.org/api/long_polling/'
    timestamp = ''

    while True:
        try:
            data = {'timestamp': timestamp}
            response = requests.get(long_poll_url, headers=headers, data=data)
            revies = response.json()
            if revies['status'] == 'timeout':
                timestamp = revies['timestamp_to_request']
            if revies['status'] == 'found':
                timestamp = revies['last_attempt_timestamp']
                new_attempt = revies["new_attempts"][0]
                if revies['new_attempts'][0]['is_negative']:
                    reaction = 'К работе притензий нету, стоит приступать ' \
                        'к следующему заданию'
                else:
                    reaction = 'К сожалению работа требует улучшения'
                message = dedent(
                    f'''\
                    У вас проверили работу: \"{new_attempt["lesson_title"]}\"

                    {new_attempt["lesson_url"]}

                    {reaction}
                    '''
                )
                await bot.send_message(chat_id, message)
                session = await bot.get_session()
                await session.close()
        except requests.exceptions.ReadTimeout:
            logging.error('ReadTimeout')
        except requests.exceptions.ConnectionError:
            logging.error('ConnectionError')
            asyncio.sleep(60)


if __name__ == '__main__':
    asyncio.run(main())
