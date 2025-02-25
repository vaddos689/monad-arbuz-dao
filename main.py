import sys
import itertools

import asyncio

from data.config import logger
from utils.create_files import create_files
from db_api.database import initialize_db
from utils.adjust_policy import set_windows_event_loop_policy
from data.config import EVM_PKS, PROXIES, logger
from utils.import_info import get_info
from utils.user_menu import get_action, monad_menu, apriori_menu, onchain_stats_menu
from db_api.start_import import ImportToDB
from settings.settings import ASYNC_TASK_IN_SAME_TIME
from tasks.main import get_start
from migrate import migrate
from utils.reset_count_progress import set_progress_to_zero


def main():
    global remaining_tasks

    while True:
        set_progress_to_zero()

        user_choice = get_action()

        semaphore = asyncio.Semaphore(ASYNC_TASK_IN_SAME_TIME)

        match user_choice:

            case "Import data to db":
                evm_pks = get_info(EVM_PKS)
                proxies = get_info(PROXIES)

                logger.info(f'\n\n\n'
                            f'Загружено в evm_pks.txt {len(evm_pks)} аккаунтов EVM \n'
                            f'Загружено в proxies.txt {len(proxies)} прокси \n'
                )

                cycled_proxies_list = itertools.cycle(proxies) if proxies else None

                formatted_data: list = [{
                        'evm_pk': evm_pk,
                        'proxy': next(cycled_proxies_list) if cycled_proxies_list else None,
                    } for evm_pk in evm_pks
                ]

                asyncio.run(ImportToDB.add_info_to_db(accounts_data=formatted_data))

            case "Monad":
                monad_choice = monad_menu()
                match monad_choice:
                    case "MON faucet":
                            asyncio.run(get_start(semaphore, "MON faucet"))
            
            case "Apriori": # TODO
                apriori_choice = apriori_menu()
                match apriori_choice:
                    case "Stake MON":
                        asyncio.run(get_start(semaphore, "Stake MON"))
            
            case "OnChain stats":
                  onchain_choice = onchain_stats_menu()
                  match onchain_choice:
                       case "Update MON balance":
                            asyncio.run(get_start(semaphore, "Update MON balance"))
            
            case "Exit":
                sys.exit(1)


if __name__ == "__main__":
    #try:
        # check_encrypt_param()
        asyncio.run(initialize_db())
        create_files()
        asyncio.run(migrate())
        set_windows_event_loop_policy()
        main()
    # except (SystemExit, KeyboardInterrupt):
    #     logger.info("Program closed")