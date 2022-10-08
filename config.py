from os import environ
from dotenv import load_dotenv


load_dotenv()


class Config:
    BOT_TOKEN = environ.get("BOT_TOKEN", None)
    CHAT_ID = environ.get("CHAT_ID", None)
