from data.config import logger, tasks_lock
from data.models import TokenAmount, Networks
from data.session import BaseAsyncSession

from db_api.database import Accounts

from clients.eth.eth_client import EthClient
from utils.encrypt_params import get_private_key

from tasks.base import Base

class Onchain(Base):
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


    async def _update_balance(self):
        mon_balance = TokenAmount(await self.eth_client.w3.eth.get_balance(self.data.evm_address), wei=True)
        self.data.mon_balance = float(mon_balance.Ether)
        async with tasks_lock:
            await self.write_to_db()
        logger.success(f'[{self.data.id}] | {self.data.evm_address} | успешно спарсил баланс. Текущий баланс: {mon_balance.Ether} {Networks.Monad.coin_symbol}')
        return True

    @Base.retry
    async def parse_native_balance(self):
        return await self._update_balance()