import os
import sys
import asyncio
from pathlib import Path

from loguru import logger


# Определяем путь и устанавливаем root dir
if getattr(sys, 'frozen', False):
    ROOT_DIR = Path(sys.executable).parent.absolute()
else:
    ROOT_DIR = Path(__file__).parent.parent.absolute()


# Папка status
STATUS_DIR = os.path.join(ROOT_DIR, 'status')
LOG = os.path.join(STATUS_DIR, 'log.txt')
ACCOUNTS_DB = os.path.join(STATUS_DIR, 'accounts.db')
SALT_PATH = os.path.join(STATUS_DIR, 'salt.dat')

# Импорт
IMPORT_DIR = os.path.join(ROOT_DIR, 'import')
EVM_PKS = os.path.join(IMPORT_DIR, 'evm_pks.txt')
PROXIES = os.path.join(IMPORT_DIR, 'proxies.txt')

# Abis
ABIS_DIR = os.path.join(ROOT_DIR, 'abis')
BADGE_ABI = os.path.join(ABIS_DIR, 'apriori.json')

# Создаем
IMPORTANT_FILES = [EVM_PKS, PROXIES]

# Кол-во выполненных асинхронных задач, блокировщий задач asyncio
completed_tasks = [0]
remaining_tasks = [0]
tasks_lock = asyncio.Lock()

CIPHER_SUITE = []

# Логер
logger.add(LOG, format='{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}', level='DEBUG')
