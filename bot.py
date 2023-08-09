import asyncio
import requests
import dotenv
import logging
import os
from aiogram import Bot
from textwrap import dedent


class PoolLogsHandler(logging.Handler):
    def __init__(self, bot, chat_id):
        super().__init__()
        self.bot = bot
        self.chat_id = chat_id

    def emit(self, record):
        message = self.format(record)
        asyncio.run(send_message(message, self.bot, self.chat_id))


def main():
    dotenv.load_dotenv('.env')
    tg_token = os.environ['TELEGRAM_TOKEN']
    dvmn_token = os.environ['DEVMAN_TOKEN']
    chat_id = int(os.environ['TELEGRAM_CHAT_ID'])
    bot = Bot(token=tg_token)
    logging.basicConfig(
        level=logging.ERROR
        )
    logger = logging.getLogger('Pool logger')
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
                asyncio.run(send_message(message, bot, chat_id))
        except requests.exceptions.ReadTimeout:
            logger.error('ReadTimeout')
        except requests.exceptions.ConnectionError:
            logger.error('ConnectionError')
            asyncio.sleep(60)


async def send_message(message, bot, chat_id):
    await bot.send_message(chat_id, message)
    session = await bot.get_session()
    await session.close()


if __name__ == '__main__':
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    main()
