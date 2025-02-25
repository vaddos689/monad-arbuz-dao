import random
import json
import uuid
import asyncio
import secrets

from eth_account.messages import encode_defunct
from eth_keys import keys
from db_api.database import Accounts
from data.session import BaseAsyncSession
from data.config import logger, tasks_lock, BADGE_ABI
from clients.eth.eth_client import EthClient
from utils.encrypt_params import get_private_key
from utils.get_amount import get_amount
from tasks.base import Base
from datetime import datetime, timezone
from data.models import TokenAmount, Networks, APRIORI_STAKE_CONTRACT
from data.eth_convertor import TxArgs
from web3.types import TxParams

from settings.settings import APRIORI_STAKE_AMOUNT_RANGE

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

    @Base.retry
    async def stake_mon(self):
        stake_amount = TokenAmount(get_amount(APRIORI_STAKE_AMOUNT_RANGE), wei=False)
        mon_balance = TokenAmount(await self.eth_client.w3.eth.get_balance(self.data.evm_address), wei=True)

        logger.info(f'[{self.data.id}] | {self.data.evm_address} | текущий баланс: {mon_balance.Ether} {Networks.Monad.coin_symbol}')
        if float(mon_balance.Ether) < float(stake_amount.Ether):
            logger.error(f'[{self.data.id}] | {self.data.evm_address} | текущего баланса не достаточно')
            return True
        
        apriori_contract = self.eth_client.w3.eth.contract(address=self.eth_client.w3.to_checksum_address(APRIORI_STAKE_CONTRACT), abi=json.load(open(BADGE_ABI)))

        encoded_data = apriori_contract.encodeABI(
            fn_name="deposit",
            args=[stake_amount.Wei, self.data.evm_address]
        )

        transaction = {
            "chainId": Networks.Monad.chain_id,
            "from": self.data.evm_address,
            "to": APRIORI_STAKE_CONTRACT,
            "data": encoded_data,
            "value": stake_amount.Wei
        }
        
        logger.info(f'[{self.data.id}] | {self.data.evm_address} | стейкаю {stake_amount.Ether} {Networks.Monad.coin_symbol}')
        tx = await self.eth_client.transactions.sign_and_send(tx_params=transaction)
        receipt = await tx.wait_for_receipt(client=self.eth_client, timeout=300)
        if receipt:
            logger.success(f'[{self.data.id}] | {self.data.evm_address} | Успешно застейкал {stake_amount.Ether} {Networks.Monad.coin_symbol}. Tx hash: {tx.hash.hex()}')
            return True
