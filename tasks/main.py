import asyncio
import traceback
import random

from data.config import logger, tasks_lock, completed_tasks, remaining_tasks
from db_api.models import Accounts
from db_api.database import get_accounts
from settings.settings import SLEEP_BEETWEEN_ACTIONS, ACCOUNT_SHUFFLE
from tqdm import tqdm
from tasks.monad_xyz import MonadXyz
from tasks.apriori import Apriori
from tasks.onchain import Onchain
from data.models import Networks


async def get_start(semaphore, quest: str):
    #try:
        if isinstance(quest, str):
            accounts: list[Accounts] = await get_accounts(quest)

            # ДЛЯ ОПРЕДЛЕННОГО АККА
            # all_accounts: list[Accounts] = await get_accounts(quest)
            # accounts = []
            # for address in all_accounts:
            #     if address.evm_address == "":
            #         accounts.append(address)
            #         break

        else:
            accounts: list[dict] = quest
            
        
        if len(accounts) != 0:
            if ACCOUNT_SHUFFLE:
                random.shuffle(accounts)
            logger.info(f'Всего задач: {len(accounts)}')
            tasks = []
            if isinstance(quest, str):
                for account_data in accounts:
                    task = asyncio.create_task(start_limited_task(semaphore, accounts, account_data, quest=quest))
                    tasks.append(task)
            else:
                account_number = 1
                for account_data in accounts:
                    task = asyncio.create_task(start_limited_task(semaphore, accounts, account_data, quest=account_number))
                    tasks.append(task)
                    account_number += 1
            await asyncio.wait(tasks)
        else:
            msg = (f'Не удалось начать действие, причина: нет подходящих аккаунтов для выбранного действия.')
            logger.warning(msg)
    # except Exception as e:
    #     pass

async def start_limited_task(semaphore, accounts, account_data, quest):
    #try:
        async with semaphore:
            status = await start_task(account_data, quest)
            async with tasks_lock:
                completed_tasks[0] += 1
                remaining_tasks[0] = len(accounts) - completed_tasks[0]

            logger.warning(f'Всего задач: {len(accounts)}. Осталось задач: {remaining_tasks[0]}')

            if isinstance(quest, str):
                if remaining_tasks[0] > 0 and status:
                    # Генерация случайного времени ожидания
                    sleep_time = random.randint(SLEEP_BEETWEEN_ACTIONS[0], SLEEP_BEETWEEN_ACTIONS[1])

                    logger.info(f"Ожидание {sleep_time} между действиями...")
                    
                    await asyncio.sleep(sleep_time)

async def start_task(account_data, quest):
    if isinstance(quest, str):
        # Monad xyz
        if quest in {"MON faucet"}:
            async with MonadXyz(data=account_data) as monad:
                return await monad.claim_faucet()
        
        # OnChain stats
        if quest in {"Update MON balance"}:
            async with Onchain(data=account_data, network=Networks.Monad) as onchain:
                return await onchain.parse_native_balance()

        # Apriori
        if quest in {"Stake MON"}:
            async with Apriori(data=account_data, network=Networks.Monad) as apriori:
                return await apriori.stake_mon()
