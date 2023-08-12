import asyncio
import requests
import dotenv
import logging
import os
from aiogram import Bot
from textwrap import dedent


logger = logging.getLogger('pool')


class PoolLogsHandler(logging.Handler):

    def __init__(self, bot, chat_id):
        super().__init__()
        self.bot = bot
        self.chat_id = chat_id

    def emit(self, record):
        message = self.format(record)
        asyncio.run(self.bot.send_message(self.chat_id, message))


def main():

    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    dotenv.load_dotenv('.env')
    tg_token = os.environ['TELEGRAM_TOKEN']
    dvmn_token = os.environ['DEVMAN_TOKEN']
    chat_id = int(os.environ['TELEGRAM_CHAT_ID'])
    bot = Bot(token=tg_token)
    logger.setLevel('INFO')
    logger.addHandler(PoolLogsHandler(bot, chat_id))
    headers = {'Authorization': dvmn_token}
    long_poll_url = 'https://dvmn.org/api/long_polling/'
    timestamp = ''
    logger.info('long_pool start')
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
                    reaction = 'К сожалению работа требует улучшения'
                else:
                    reaction = 'К работе притензий нету, стоит приступать ' \
                        'к следующему заданию'
                message = dedent(
                    f'''\
                    У вас проверили работу: \"{new_attempt["lesson_title"]}\"

                    {new_attempt["lesson_url"]}

                    {reaction}
                    '''
                )
                asyncio.run(bot.send_message(chat_id, message))
        except requests.exceptions.ReadTimeout:
            logger.error('ReadTimeout')
        except requests.exceptions.ConnectionError:
            logger.error('ConnectionError')
            asyncio.sleep(60)


if __name__ == '__main__':
    main()
