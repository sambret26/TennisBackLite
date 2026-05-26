import os
from datetime import datetime
from pytz import timezone
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '../../.env'))
timezone = timezone(os.getenv('TIME_ZONE'))

BATCH = '[BATCH]'
DISCORD = '[DISCORD]'
BOT = '[BOT]'
CONFIG = '[CONFIG]'
MOJA = '[MOJA]'

class Log:

    def info(self, type, message):
        self.logPrint(f"[INFO] - {type} - {message}")

    def warn(self, type, message):
        self.logPrint(f"[WARN] - {type} - {message}")

    def error(self, type, message):
        self.logPrint(f"[ERROR] - {type} - {message}")

    def logPrint(self, message):
        currentTime = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S")
        message = f"[{currentTime}] - {message}"
        print(message)

log = Log()