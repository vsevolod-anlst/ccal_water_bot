from dotenv import load_dotenv
import os
import logging


logging.basicConfig(level=logging.DEBUG)
aiohttp_logger = logging.getLogger("aiohttp")
aiohttp_logger.setLevel(logging.DEBUG)


load_dotenv()
token = os.getenv('TELEGRAM_BOT_TOKEN')

# if not API_TOKEN or not CURRENCY_API_KEY:
#     raise NameError