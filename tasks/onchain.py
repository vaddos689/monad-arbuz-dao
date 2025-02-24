from data.config import logger, tasks_lock
from data.models import TokenAmount, Networks

from tasks.base import Base

class Onchain(Base):
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