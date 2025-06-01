from typing import List
import requests
import json
from eth_account import Account
from web3 import Web3
import time

from utils.erc20 import erc20_balance, erc20_allowance, ERC20_ABI


 # IoTeX 测试网 RPC 端点
testnet_rpc = "https://babel-api.testnet.iotex.io"
web3 = Web3(Web3.HTTPProvider(testnet_rpc))
chain_id = 4690
polyagent_token_contract = "0xD3286E20Ff71438D9f6969828F7218af4A375e2f" 

sender_private_key = "e4ad52fbc8c6fe3f4069af70363b24ca4453dbf472d92f83a8adf38e8010991f"
sender_address = Account.from_key('0x' + sender_private_key).address

spender_private_key = "3efe78303dcf8ea3355ef363f04eb442e000081fe66ebcebf5d9cf19f3ace8b8"
spender_address = Account.from_key('0x' + spender_private_key).address
print(sender_address)
print(spender_address)
print("----------------------------------------------")

balance_info = erc20_balance(
    token_contract_address=polyagent_token_contract,
    wallet_address=sender_address,
    decimals=18
)

allowance_info = erc20_allowance(
    token_contract_address=polyagent_token_contract,
    owner_address=sender_address,
    spender_address=spender_address,
)

print(json.dumps(balance_info, indent=4))
print("----------------------------------------------")
print(json.dumps(allowance_info,indent=4))
print("----------------------------------------------")
