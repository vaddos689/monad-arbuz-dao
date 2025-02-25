from datetime import datetime, timezone, timedelta

from sqlalchemy.future import select

from settings.settings import APRIORI_STAKE_AMOUNT_RANGE
from db_api import sqlalchemy_
from db_api.models import Accounts, Base
from data.config import ACCOUNTS_DB
from typing import List, Optional


db = sqlalchemy_.DB(f'sqlite+aiosqlite:///{ACCOUNTS_DB}', pool_recycle=3600, connect_args={'check_same_thread': False})


async def get_account(evm_pk: str) -> Optional[Accounts]:
    return await db.one(Accounts, Accounts.evm_pk == evm_pk)

async def get_accounts(
        quest: str
) -> List[Accounts]:
    
    today = datetime.now(timezone.utc).date()

    if quest in {"MON Faucet"}: # Monad xyz
        now = datetime.now(timezone.utc)
        utc_now = now.replace(tzinfo=None)
        query = select(Accounts).where(
            Accounts.mon_faucet <= utc_now - timedelta(hours=24),
            Accounts.finished == False
        )

    elif quest in {"Stake MON"}: # Apriori
        query = select(Accounts).where(
            Accounts.mon_balance > 0,
            Accounts.finished == False
        )

    elif quest in {"Update MON balance"}:
        query = select(Accounts).where(
        Accounts.finished == False
        )
    # elif quest in {"Gobi Desert - Social Media"}: 
    #     query = select(Accounts).where(
    #         Accounts.gobi_desert_social_media == False,
    #         Accounts.finished == False
    #     )

    # elif quest in {"Unlink bad Twitter token from Galxe"}:
    #     query = select(Accounts).where(
    #         Accounts.twitter_account_status != 'OK',
    #         Accounts.finished == False
    #     )
    
    # elif quest in {"SaharaAI Parse ShardAmount"}:
    #     query = select(Accounts).where(
    #         Accounts.sahara_shard_amount == 0,
    #         Accounts.finished == False
    #     )
        
    # elif quest in {"SaharaAI Parse Native Balance"}:
    #     query = select(Accounts).where(
    #         Accounts.finished_parse_sahara_balance == False,
    #         Accounts.finished == False
    #     )

    # elif quest in {"SaharaAI - Daily Gobi Desert (on-chain)"}:
    #     query = select(Accounts).where(
    #         Accounts.sahara_onchain_daily < today,
    #         Accounts.sahara_balance > 0,
    #         Accounts.finished == False
    #     )
    # elif quest in {"Account registration in Data Services Platform"}:
    #     query = select(Accounts).where(
    #         Accounts.account_registration_in_DSP == False,
    #         Accounts.finished == False
    #     )

    else:
        query = select(Accounts)   
    return await db.all(query)

async def initialize_db():
    await db.create_tables(Base)
