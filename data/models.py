import asyncio
from typing import Union, Optional, Dict, Any, Tuple
from dataclasses import dataclass

from hexbytes import HexBytes
from web3 import Web3
from eth_typing import ChecksumAddress
from web3.contract import AsyncContract
from web3.types import TxReceipt, _Hash32, TxParams
from eth_account.datastructures import SignedTransaction
from data.auto_repr import AutoRepr
from data.eth_convertor import GWei, Wei, TokenAmount
from data.config import logger
from data.types import Web3Async
from data import exceptions, types

APRIORI_STAKE_CONTRACT = "0xb2f82D0f38dc453D596Ad40A37799446Cc89274A"

MONAD_TOKENS = { # TODO
    # 'ETH': {
    #     'token_address': 'So11111111111111111111111111111111111111112'
    # },
    # 'SOL': {
    #     'token_address': 'BeRUj3h7BqkbdfFU7FBNYbodgf8GCHodzKvF9aVjNNfL',
    #     'token_program': 'TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb'
    # },
    # 'USDC': {
    #     'token_address': 'AKEWE7Bgh87GPp171b4cJPSSZfmZwQ3KaqYqXoKLNAEE',
    #     'token_program': 'TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb'
    # },
    # 'USDT': {
    #     'token_address': 'CEBP3CqAbW4zdZA57H2wfaSG1QNdzQ72GiQEbQXyW9Tm',
    #     'token_program': 'TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb'
    # },
    # 'USDT': {
    #     'token_address': 'CEBP3CqAbW4zdZA57H2wfaSG1QNdzQ72GiQEbQXyW9Tm',
    #     'token_program': 'TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb'
    # },
    # 'tETH': {
    #     'token_address': 'GU7NS9xCwgNPiAdJ69iusFrRfawjDDPjeMBovhV1d4kn',
    #     'token_program': 'TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb'
    # }
}


class Network:
    def __init__(self, name: str, rpc: str, chain_id: Optional[int] = None, tx_type: int = 0,
                 coin_symbol: Optional[str] = None, explorer: Optional[str] = None
                 ) -> None:
        self.name: str = name.lower()
        self.rpc: str = rpc
        self.chain_id: Optional[int] = chain_id
        self.tx_type: int = tx_type
        self.coin_symbol: Optional[str] = coin_symbol
        self.explorer: Optional[str] = explorer

        if self.coin_symbol:
            self.coin_symbol = self.coin_symbol.upper()


class Networks:
    # Mainnets
    Ethereum = Network(
        name='Ethereum',
        rpc='https://rpc.ankr.com/eth/',
        chain_id=1,
        tx_type=2,
        coin_symbol='ETH',
        explorer='https://etherscan.io/tx/',
    )

    Arbitrum = Network(
        name='Arbitrum',
        rpc='https://rpc.ankr.com/arbitrum/',
        chain_id=42161,
        tx_type=2,
        coin_symbol='ETH',
        explorer='https://arbiscan.io/tx/',
    )

    Optimism = Network(
        name='Optimism',
        rpc='https://rpc.ankr.com/optimism/',
        chain_id=10,
        tx_type=2,
        coin_symbol='ETH',
        explorer='https://optimistic.etherscan.io/tx/',
    )

    Base = Network(
        name='Base',
        rpc='https://base-rpc.publicnode.com/',
        chain_id=8453,
        tx_type=2,
        coin_symbol='ETH',
        explorer='https://basescan.org/',
    )

    # Testnets
    Goerli = Network(
        name='Goerli',
        rpc='https://rpc.ankr.com/eth_goerli/',
        chain_id=5,
        tx_type=2,
        coin_symbol='ETH',
        explorer='https://goerli.etherscan.io/tx/',
    )

    Monad = Network(
        name='Monad Testnet',
        rpc='https://testnet-rpc.monad.xyz/',
        chain_id=10143,
        tx_type=0,
        coin_symbol='MON',
        explorer='http://testnet.monadexplorer.com/tx/',
    )


@dataclass
class DefaultABIs:
    Token = [
        {
            'constant': True,
            'inputs': [],
            'name': 'name',
            'outputs': [{'name': '', 'type': 'string'}],
            'payable': False,
            'stateMutability': 'view',
            'type': 'function'
        },
        {
            'constant': True,
            'inputs': [],
            'name': 'symbol',
            'outputs': [{'name': '', 'type': 'string'}],
            'payable': False,
            'stateMutability': 'view',
            'type': 'function'
        },
        {
            'constant': True,
            'inputs': [],
            'name': 'totalSupply',
            'outputs': [{'name': '', 'type': 'uint256'}],
            'payable': False,
            'stateMutability': 'view',
            'type': 'function'
        },
        {
            'constant': True,
            'inputs': [],
            'name': 'decimals',
            'outputs': [{'name': '', 'type': 'uint256'}],
            'payable': False,
            'stateMutability': 'view',
            'type': 'function'
        },
        {
            'constant': True,
            'inputs': [{'name': 'who', 'type': 'address'}],
            'name': 'balanceOf',
            'outputs': [{'name': '', 'type': 'uint256'}],
            'payable': False,
            'stateMutability': 'view',
            'type': 'function'
        },
        {
            'constant': True,
            'inputs': [{'name': '_owner', 'type': 'address'}, {'name': '_spender', 'type': 'address'}],
            'name': 'allowance',
            'outputs': [{'name': 'remaining', 'type': 'uint256'}],
            'payable': False,
            'stateMutability': 'view',
            'type': 'function'
        },
        {
            'constant': False,
            'inputs': [{'name': '_spender', 'type': 'address'}, {'name': '_value', 'type': 'uint256'}],
            'name': 'approve',
            'outputs': [],
            'payable': False,
            'stateMutability': 'nonpayable',
            'type': 'function'
        },
        {
            'constant': False,
            'inputs': [{'name': '_to', 'type': 'address'}, {'name': '_value', 'type': 'uint256'}],
            'name': 'transfer',
            'outputs': [], 'payable': False,
            'stateMutability': 'nonpayable',
            'type': 'function'
        }]


class Wallet:
    def __init__(self, client) -> None:
        self.client = client

    async def balance(self, token_address: Optional[str] = None,
                      address: Optional[ChecksumAddress] = None) -> Union[Wei, TokenAmount]:
        if not address:
            address = self.client.account.address

        address = Web3.to_checksum_address(address)
        if not token_address:
            return Wei(await self.client.w3.eth.get_balance(account=address))

        token_address = Web3.to_checksum_address(token_address)
        contract = await self.client.contracts.get_contract(contract_address=token_address)
        return TokenAmount(
            amount=await contract.functions.balanceOf(address).call(),
            decimals=await contract.functions.decimals().call(),
            wei=True
        )

    async def nonce(self, address: Optional[ChecksumAddress] = None) -> int:
        if not address:
            address = self.client.account.address
        return await self.client.w3.eth.get_transaction_count(address)

class Contracts:
    def __init__(self, client) -> None:
        self.client = client

    async def get_contract(self,
                           contract_address: ChecksumAddress,
                           abi: Union[list, dict] = DefaultABIs
                           ) -> AsyncContract:
        return self.client.w3.eth.contract(address=contract_address, abi=abi)

class Tx(AutoRepr):
    """
    An instance of transaction for easy execution of actions on it.

    Attributes:
        hash (Optional[_Hash32]): a transaction hash.
        params (Optional[dict]): the transaction parameters.
        receipt (Optional[TxReceipt]): a transaction receipt.
        function_identifier (Optional[str]): a function identifier.
        input_data (Optional[Dict[str, Any]]): an input data.

    """
    hash: Optional[_Hash32]
    params: Optional[dict]
    receipt: Optional[TxReceipt]
    function_identifier: Optional[str]
    input_data: Optional[Dict[str, Any]]

    def __init__(self, tx_hash: Optional[Union[str, _Hash32]] = None, params: Optional[dict] = None) -> None:
        """
        Initialize the class.

        Args:
            tx_hash (Optional[Union[str, _Hash32]]): the transaction hash. (None)
            params (Optional[dict]): a dictionary with transaction parameters. (None)

        """
        if not tx_hash and not params:
            raise exceptions.TransactionException("Specify 'tx_hash' or 'params' argument values!")

        if isinstance(tx_hash, str):
            tx_hash = HexBytes(tx_hash)

        self.hash = tx_hash
        self.params = params
        self.receipt = None
        self.function_identifier = None
        self.input_data = None

    async def parse_params(self, client) -> Dict[str, Any]:
        """
        Parse the parameters of a sent transaction.

        Args:
            client (Client): the Client instance.

        Returns:
            Dict[str, Any]: the parameters of a sent transaction.

        """
        tx_data = await client.w3.eth.get_transaction(transaction_hash=self.hash)
        self.params = {
            'chainId': client.network.chain_id,
            'nonce': int(tx_data.get('nonce')),
            'gasPrice': int(tx_data.get('gasPrice')),
            'gas': int(tx_data.get('gas')),
            'from': tx_data.get('from'),
            'to': tx_data.get('to'),
            'data': tx_data.get('input'),
            'value': int(tx_data.get('value'))
        }
        return self.params

    async def decode_input_data(
            self, client, contract: types.Contract
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Decode the input data of a sent transaction.

        Args:
            client (Client): the Client instance.
            contract (Contract): the contract instance whose ABI will be used to decode input data.

        Returns:
            Tuple[Optional[str], Optional[Dict[str, Any]]]: the function identifier and decoded input data
                of a sent transaction.

        """
        if not self.params or not self.params.get('data'):
            await self.parse_params(client=client)

        try:
            self.function_identifier, self.input_data = await Transactions.decode_input_data(
                client=client, contract=contract, input_data=self.params.get('data')
            )

        except:
            pass

        return self.function_identifier, self.input_data

    async def wait_for_receipt(
            self, client, timeout: Union[int, float] = 120, poll_latency: float = 0.1
    ) -> Dict[str, Any]:
        """
        Wait for the transaction receipt.

        Args:
            client (Client): the Client instance.
            timeout (Union[int, float]): the receipt waiting timeout. (120 sec)
            poll_latency (float): the poll latency. (0.1 sec)

        Returns:
            Dict[str, Any]: the transaction receipt.

        """
        self.receipt = dict(await client.w3.eth.wait_for_transaction_receipt(
            transaction_hash=self.hash, timeout=timeout, poll_latency=poll_latency
        ))
        return self.receipt

    async def cancel(
            self, client, gas_price: Optional[types.GasPrice] = None,
            gas_limit: Optional[types.GasLimit] = None
    ) -> bool:
        """
        Cancel the transaction.

        Args:
            client (Client): the Client instance.
            gas_price (Optional[GasPrice]): the gas price in GWei. (parsed from the network)
            gas_limit (Optional[GasLimit]): the gas limit in Wei. (parsed from the network)

        Returns:
            bool: True if the transaction was sent successfully.

        """
        if self.params and 'nonce' in self.params:
            if not gas_price:
                gas_price = (await Transactions.gas_price(w3=client.w3)).Wei

            elif isinstance(gas_price, (int, float)):
                gas_price = GWei(gas_price).Wei

            if gas_price < self.params.get('gasPrice') * 1.11:
                gas_price = int(self.params.get('gasPrice') * 1.11)

            tx_params = {
                'chainId': client.network.chain_id,
                'nonce': self.params.get('nonce'),
                'to': client.account.address,
                'value': 0
            }
            if client.network.tx_type == 2:
                tx_params['maxPriorityFeePerGas'] = (await client.transactions.max_priority_fee(w3=client.w3)).Wei
                tx_params['maxFeePerGas'] = gas_price + tx_params['maxPriorityFeePerGas']

            else:
                tx_params['gasPrice'] = gas_price

            if not gas_limit:
                gas_limit = await Transactions.estimate_gas(w3=client.w3, tx_params=tx_params)

            elif isinstance(gas_limit, int):
                gas_limit = Wei(gas_limit)

            tx_params['gas'] = gas_limit.Wei
            signed_tx = client.w3.eth.account.sign_transaction(
                transaction_dict=tx_params, private_key=client.account.key
            )
            tx_hash = await client.w3.eth.send_raw_transaction(transaction=signed_tx.rawTransaction)
            if tx_hash:
                self.hash = tx_hash
                self.params = tx_params.copy()
                return True

        return False

    async def speed_up(
            self, client, gas_price: Optional[types.GasPrice] = None, gas_limit: Optional[types.GasLimit] = None
    ) -> bool:
        """
        Speed up the transaction.

        Args:
            client (Client): the Client instance.
            gas_price (Optional[GasPrice]): the gas price in GWei. (parsed from the network * 1.5)
            gas_limit (Optional[GasLimit]): the gas limit in Wei. (parsed from the network)

        Returns:
            bool: True if the transaction was sent successfully.

        """
        if self.params and 'nonce' in self.params:
            if not gas_price:
                gas_price = int((await Transactions.gas_price(w3=client.w3)).Wei * 1.5)

            elif isinstance(gas_price, (int, float)):
                gas_price = GWei(gas_price).Wei

            tx_params = self.params.copy()
            if client.network.tx_type == 2:
                tx_params['maxPriorityFeePerGas'] = (await client.transactions.max_priority_fee(w3=client.w3)).Wei
                tx_params['maxFeePerGas'] = gas_price + tx_params['maxPriorityFeePerGas']

            else:
                tx_params['gasPrice'] = gas_price

            if not gas_limit:
                gas_limit = await Transactions.estimate_gas(w3=client.w3, tx_params=tx_params)

            elif isinstance(gas_limit, int):
                gas_limit = Wei(gas_limit)

            tx_params['gas'] = gas_limit.Wei
            signed_tx = client.w3.eth.account.sign_transaction(
                transaction_dict=tx_params, private_key=client.account.key
            )
            tx_hash = await client.w3.eth.send_raw_transaction(transaction=signed_tx.rawTransaction)
            if tx_hash:
                self.hash = tx_hash
                self.params = tx_params.copy()
                return True

        return False

class Transactions:
    def __init__(self, client):
        self.client = client

    @staticmethod
    async def max_priority_fee(w3: Web3Async) -> Wei:
        """
        Get the current max priority fee.

        Args:
            w3 (Web3): the Web3 instance.

        Returns:
            Wei: the current max priority fee.

        """
        return Wei(await w3.eth.max_priority_fee)

    @staticmethod
    async def estimate_gas(w3: Web3Async, tx_params: TxParams) -> Wei:
        """
        Get the estimate gas limit for a transaction with specified parameters.

        Args:
            w3 (Web3): the Web3 instance.
            tx_params (TxParams): parameters of the transaction.

        Returns:
            Wei: the estimate gas.

        """
        return Wei(await w3.eth.estimate_gas(transaction=tx_params))

    async def auto_add_params(self, tx_params: TxParams) -> TxParams:
        """
        Add 'chainId', 'nonce', 'from', 'gasPrice' or 'maxFeePerGas' + 'maxPriorityFeePerGas' and 'gas' parameters to
            transaction parameters if they are missing.

        Args:
            tx_params (TxParams): parameters of the transaction.

        Returns:
            TxParams: parameters of the transaction with added values.

        """
        if 'chainId' not in tx_params:
            tx_params['chainId'] = self.client.network.chain_id

        if 'nonce' not in tx_params:
            tx_params['nonce'] = await self.client.wallet.nonce()

        if 'from' not in tx_params:
            tx_params['from'] = self.client.account.address

        if 'gasPrice' not in tx_params and 'maxFeePerGas' not in tx_params:
            gas_price = (await self.gas_price(w3=self.client.w3)).Wei
            if self.client.network.tx_type == 2:
                tx_params['maxFeePerGas'] = gas_price

            else:
                tx_params['gasPrice'] = gas_price

        elif 'gasPrice' in tx_params and not int(tx_params['gasPrice']):
            tx_params['gasPrice'] = (await self.gas_price(w3=self.client.w3)).Wei

        if 'maxFeePerGas' in tx_params and 'maxPriorityFeePerGas' not in tx_params:
            tx_params['maxPriorityFeePerGas'] = (await self.max_priority_fee(w3=self.client.w3)).Wei
            tx_params['maxFeePerGas'] = tx_params['maxFeePerGas'] + tx_params['maxPriorityFeePerGas']

        if 'gas' not in tx_params or not int(tx_params['gas']):
            tx_params['gas'] = (await self.estimate_gas(w3=self.client.w3, tx_params=tx_params)).Wei

        return tx_params

    async def sign_and_send(self, tx_params: TxParams) -> Tx:
        """
        Sign and send a transaction. Additionally, add 'chainId', 'nonce', 'from', 'gasPrice' or
            'maxFeePerGas' + 'maxPriorityFeePerGas' and 'gas' parameters to transaction parameters if they are missing.

        Args:
            tx_params (TxParams): parameters of the transaction.

        Returns:
            Tx: the instance of the sent transaction.

        """
        await self.auto_add_params(tx_params=tx_params)
        signed_tx = await self.sign_transaction(tx_params)
        tx_hash = await self.client.w3.eth.send_raw_transaction(transaction=signed_tx.rawTransaction)
        return Tx(tx_hash=tx_hash, params=tx_params)

    @staticmethod
    async def gas_price(w3: Web3, max_retries=30) -> Wei:
        retries = 0
        while retries < max_retries:
            try:
                return Wei(await w3.eth.gas_price)
            except asyncio.exceptions.TimeoutError:
                logger.debug(f"Retry {retries + 1}/{max_retries} due to TimeoutError ETH gas price")
                retries += 1

        raise ValueError(f"Unable to get gas price after {max_retries} retries")

    async def sign_transaction(self, tx_params: TxParams) -> SignedTransaction:
        """
        Sign a transaction.

        Args:
            tx_params (TxParams): parameters of the transaction.

        Returns:
            SignedTransaction: the signed transaction.

        """
        return self.client.w3.eth.account.sign_transaction(
            transaction_dict=tx_params, private_key=self.client.account.key
        )
