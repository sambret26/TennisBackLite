import os
from dotenv import load_dotenv
from infrastructure.logger.logger import log, CONFIG


# Charge les variables d'environnement depuis le fichier .env
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SECRET_KEY = os.getenv('SECRET_KEY')
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    DISCORD_GUILD_ID = os.getenv('DISCORD_GUILD_ID')
    TIME_ZONE = os.getenv('TIME_ZONE')

    def __init__(self):
        if self.SQLALCHEMY_DATABASE_URI is None:
            log.warn(CONFIG, "DATABASE_URL is not set in .env file")
