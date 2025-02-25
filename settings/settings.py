import os
import ast

from dotenv import load_dotenv
from data.config import logger
from distutils.util import strtobool

load_dotenv(dotenv_path='.env')

try:
    # КОЛ-ВО ПОПЫТОК
    NUMBER_OF_ATTEMPTS: int = int(os.getenv('NUMBER_OF_ATTEMPTS'))

    # Одновременное кол-во асинхронных задач
    ASYNC_TASK_IN_SAME_TIME: int = int(os.getenv('ASYNC_TASK_IN_SAME_TIME'))

    # ключи от сервисов капчи
    SERVICE_TO_USE: str = str(os.getenv('SERVICE_TO_USE'))
    API_KEY_CAPSOLVER: str = str(os.getenv('API_KEY_CAPSOLVER'))

    # SLEEP BEETWEEN ACTION
    SLEEP_FROM: int = int(os.getenv('SLEEP_FROM'))
    SLEEP_TO: int = int(os.getenv('SLEEP_TO'))
    SLEEP_BEETWEEN_ACTIONS: list = [SLEEP_FROM, SLEEP_TO]

    ACCOUNT_SHUFFLE: bool = bool(strtobool(os.getenv('ACCOUNT_SHUFFLE'))) 
    MIN_BALANCE = float(os.getenv('MIN_BALANCE'))

    # Apriori
    APRIORI_STAKE_AMOUNT_RANGE = os.getenv('APRIORI_STAKE_AMOUNT_RANGE')
    if APRIORI_STAKE_AMOUNT_RANGE:
        APRIORI_STAKE_AMOUNT_RANGE = ast.literal_eval(APRIORI_STAKE_AMOUNT_RANGE) 


except TypeError:
    logger.warning('Вы не создали .env и не добавили туда настройки')