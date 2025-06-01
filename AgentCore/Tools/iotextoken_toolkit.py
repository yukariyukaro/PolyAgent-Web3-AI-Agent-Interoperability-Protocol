from camel.toolkits.base import BaseToolkit
from camel.toolkits.function_tool import FunctionTool

from typing import List
import requests
import json
from eth_account import Account
from web3 import Web3
import time

class IotexTokenToolkit(BaseToolkit):
    def __init__(self, rpc_url: str, erc20_abi: list):
        """
        Initializes the toolkit with a given RPC URL and ERC20 ABI.

        Args:
            rpc_url (str): The RPC URL for the IoTeX testnet
            erc20_abi (list): The ABI definition for the ERC20 contract
        """
        self.rpc_url = rpc_url
        self.web3 = Web3(Web3.HTTPProvider(self.rpc_url))
        self.erc20_abi = erc20_abi

    def erc20_balance(self, token_contract_address: str, wallet_address: str, decimals: int = 18) -> dict:
        """
        Queries the ERC20 token balance of a specified wallet address.

        Args:
            token_contract_address (str): The ERC20 token contract address
            wallet_address (str): The wallet address to query
            decimals (int, optional): Token decimals (default is 18)

        Returns:
            dict: A dictionary containing balance information.
        """
        try:
            if not self.web3.is_connected():
                return {
                    'success': False,
                    'error': 'Unable to connect to IoTeX testnet'
                }

            contract = self.web3.eth.contract(
                address=self.web3.to_checksum_address(token_contract_address),
                abi=self.erc20_abi
            )

            balance_wei = contract.functions.balanceOf(
                self.web3.to_checksum_address(wallet_address)
            ).call()

            balance_tokens = balance_wei / (10 ** decimals)

            return {
                'success': True,
                'balance_wei': balance_wei,
                'balance_tokens': balance_tokens,
                'wallet_address': wallet_address,
                'contract_address': token_contract_address,
                'decimals': decimals
            }

        except Exception as e:
            return {
                'success': False,
                'wallet_address': wallet_address,
                'contract_address': token_contract_address,
                'error': f"Failed to query balance: {str(e)}"
            }

    def get_tools(self) -> List[FunctionTool]:
        """
        Returns a list of FunctionTool objects representing the
        functions in the toolkit.
        """
        return [
            FunctionTool(self.erc20_balance),
        ]