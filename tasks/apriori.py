import random
import uuid
import asyncio
import secrets

from eth_account.messages import encode_defunct
from eth_keys import keys

from db_api.database import Accounts
from data.session import BaseAsyncSession
from data.config import logger, tasks_lock
from clients.eth.eth_client import EthClient
from utils.encrypt_params import get_private_key
from tasks.base import Base
from datetime import datetime, timezone
from data.models import TokenAmount, Networks                      

class Apriori(Base):
    def __init__(self, data: Accounts, async_session: BaseAsyncSession | None = None, eth_client: EthClient | None = None, network=Networks.Ethereum):
        super().__init__(data=data, async_session=async_session)

        self.version = self.data.user_agent.split('Chrome/')[1].split('.')[0]
        self.platform = self.data.user_agent.split(' ')[1][1:].replace(';', '')
        if self.platform == "Macintosh":
            self.platform = "MacOS"
        elif self.platform == "X11":
            self.platform = "Linux"

        if eth_client:
            self.eth_client = eth_client
        else:
            self.eth_client = EthClient(
                private_key=get_private_key(data), network=network, proxy=self.data.proxy, user_agent=self.data.user_agent
            )

    async def stake_mon(self):
        print("STAKE MON FUNC START")
        
    # def get_main_headers(self):
    #     return {
    #         "accept": "*/*",
    #         "accept-language": "en-US,en;q=0.9",
    #         "content-type": "application/json",
    #         "origin": "https://testnet.monad.xyz",
    #         "priority": "u=1, i",
    #         "referer": "https://testnet.monad.xyz/",
    #         "sec-ch-ua": f'"Not A(Brand";v="8", "Chromium";v="{self.version}", "Google Chrome";v="{self.version}"',
    #         "sec-ch-ua-mobile": "?0",
    #         "sec-ch-ua-platform": f'"{self.platform}"',
    #         "sec-fetch-dest": "empty",
    #         "sec-fetch-mode": "cors",
    #         "sec-fetch-site": "same-origin",
    #         "user-agent": self.data.user_agent,
    #     }
    
    # async def faucet_token_request(self, cf_turnstile_response):
    #     headers = self.get_main_headers()

    #     visitor_id = secrets.token_hex(16)

    #     json_data = {
    #         "address": self.data.evm_address,
    #         "recaptchaToken": cf_turnstile_response['gRecaptchaResponse'],
    #         "visitorId": visitor_id,
    #     }
    #     response = await self.async_session.post(
    #         'https://testnet.monad.xyz/api/claim', 
    #         headers=headers, 
    #         json=json_data,
    #         timeout=120000
    #     )  

    #     if response.status_code == 200:
    #         return True, f'[{self.data.id}] | {self.data.evm_address} | успешно сделал запрос на получение тестовых токенов. Ответ сервера: {response.json().get('message', '')}'

    #     elif response.json()["message"] == 'Claimed already, Please try again later.':
    #         return True, f'[{self.data.id}] | {self.data.evm_address} | Не смог заклеймить кран, код ответа: {response.status_code} | сообщение: {response.json().get('message', "Не смог вытащить ошибку")}'
        
    #     return False, f'[{self.data.id}] | {self.data.evm_address} | Не смог заклеймить кран, код ответа: {response.status_code} | msg: {response.text}'
    

    # @Base.retry
    # async def claim_faucet(self):
    #     captcha_solution = await Capsolver(self.data, self.async_session).wait_for_recaptcha()
    #     if captcha_solution:
    #         status, msg = await self.faucet_token_request(captcha_solution)
                  
    #         if status:
    #             self.data.mon_faucet = datetime.now(timezone.utc)
    #             async with tasks_lock:
    #                 await self.write_to_db()
    #             if "Не смог заклеймить" in msg:
    #                 logger.warning(msg)
    #             else:
    #                 logger.success(msg)
    #             return True
    #         else:
    #             logger.error(msg)
    #             return False
    #     else:
    #         logger.error(f'[{self.data.id}] | [{self.data.evm_address}] | не смог получить решение капчи...')
    #         return False
