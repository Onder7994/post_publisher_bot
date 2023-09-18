from logger import Logging
from api_methods import ApiMethods
from database import DbProcess
from time import sleep
import telebot
import configparser

BOT_CONFIG = "/opt/publisher_bot/bot_config.ini"

config_parser = configparser.ConfigParser()
config_parser.read(BOT_CONFIG)

BASE_URL = config_parser.get("wordpress", "BASE_WP_URL")
API_EP_URL = config_parser.get("wordpress", "API_EP_URL")
DB_PATH = config_parser.get("database", "DB_PATH")
DB_TABLE_NAME = config_parser.get("database", "DB_TABLE_NAME")
DB_COLUMN_NAME = config_parser.get("database", "DB_COLUMN_NAME")
BOT_TOKEN = config_parser.get("telegram", "BOT_TOKEN")
CHANNEL_ID = config_parser.get("telegram", "CHANNEL_ID")
BOT_LOGGER_NAME = config_parser.get("logger", "BOT_LOGGER_NAME")
BOT_LOGFILE = config_parser.get("logger", "BOT_LOGFILE")
SCRAPE_INTERVAL = int(config_parser.get("wordpress", "SCRAPE_INTERVAL"))

logger = Logging(BOT_LOGGER_NAME, BOT_LOGFILE)
db = DbProcess(DB_PATH, DB_COLUMN_NAME, DB_TABLE_NAME, logger)
api = ApiMethods(BASE_URL, API_EP_URL, logger, db)
bot = telebot.TeleBot(BOT_TOKEN)

def send_post_to_channel():
    post_mapping = api.get_latest_post()
    is_make_post = api.upload_post_into_db()
    if is_make_post is True:
        message = (
            f"Новая статья:\n"
            f"{post_mapping['post_title']}\n\n"
            f"{post_mapping['post_url']}\n"
        )
        bot.send_photo(CHANNEL_ID, post_mapping["post_logo"], message)
        logger.info("Пост %s успешно отправлен в канал: %s", post_mapping["post_url"], CHANNEL_ID)

def main():
    while True:
        send_post_to_channel()
        sleep(SCRAPE_INTERVAL)

if __name__ == "__main__":
    main()