import datetime

from data.auto_repr import AutoRepr
from sqlalchemy import Column, Integer, Text, Boolean, DateTime, Float
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Accounts(Base, AutoRepr):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True)

    evm_pk = Column(Text, unique=True)
    evm_address = Column(Text, unique=True)
    proxy = Column(Text)
    user_agent = Column(Text)
    
    # monad
    mon_faucet = Column(DateTime)
    mon_balance = Column(Float)

    finished = Column(Boolean)
    

    def __init__(
            self,
            evm_pk: str,
            evm_address: str,
            proxy: str,
            user_agent: str,
    ) -> None:
        
        self.evm_pk = evm_pk
        self.evm_address = evm_address
        self.proxy = proxy
        self.user_agent = user_agent

        # monad
        self.mon_faucet = datetime.datetime(1970, 1, 1)
        self.mon_balance = 0

        self.finished = False