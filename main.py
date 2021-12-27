import config
from bot import bot_api

if __name__ == '__main__':
    bot_api.telegram_bot(config.TOKEN)
