from typing import List
import requests
import json
from eth_account import Account
from web3 import Web3
import time

from utils.erc20 import erc20_balance, erc20_allowance, erc20_contract_info, erc20_approve, ERC20_ABI

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

# allowance_info = erc20_allowance(
#     token_contract_address=polyagent_token_contract,
#     owner_address=sender_address,
#     spender_address=spender_address,
# )

# contract_info = erc20_contract_info(token_contract_address=polyagent_token_contract)

# approve_info = erc20_approve(
#     private_key=sender_private_key,
#     token_contract_address=polyagent_token_contract,
#     spender_address=spender_address,
#     amount=2,
#     decimals=18
# )

# balance_info = erc20_balance(
#     token_contract_address=polyagent_token_contract,
#     wallet_address=sender_address,
#     decimals=18
# )

allowance_info = erc20_allowance(
    token_contract_address=polyagent_token_contract,
    owner_address=sender_address,
    spender_address=spender_address,
    decimals=18
)

# print(json.dumps(balance_info, indent=4))
# print("----------------------------------------------")
# print(json.dumps(allowance_info,indent=4))
# print("----------------------------------------------")
# print(json.dumps(contract_info,indent=4))
# print("----------------------------------------------")
# print(json.dumps(approve_info,indent=4))
# print("----------------------------------------------")
# print(json.dumps(balance_info, indent=4))
# print("----------------------------------------------")
print(json.dumps(allowance_info,indent=4))
