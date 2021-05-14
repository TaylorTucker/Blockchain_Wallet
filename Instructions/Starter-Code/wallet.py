# # Import dependencies
# import subprocess
# import json
# from dotenv import load_dotenv

# # Load and set environment variables
# load_dotenv()
# mnemonic=os.getenv("mnemonic")

# # Import constants.py and necessary functions from bit and web3
# # YOUR CODE HERE
 
 
# # Create a function called `derive_wallets`
# def derive_wallets(# YOUR CODE HERE):
#     command = # YOUR CODE HERE
#     p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
#     output, err = p.communicate()
#     p_status = p.wait()
#     return json.loads(output)

# # Create a dictionary object called coins to store the output from `derive_wallets`.
# coins = # YOUR CODE HERE

# # Create a function called `priv_key_to_account` that converts privkey strings to account objects.
# def priv_key_to_account(# YOUR CODE HERE):
#     # YOUR CODE HERE

# # Create a function called `create_tx` that creates an unsigned transaction appropriate metadata.
# def create_tx(# YOUR CODE HERE):
#     # YOUR CODE HERE

# # Create a function called `send_tx` that calls `create_tx`, signs and sends the transaction.
# def send_tx(# YOUR CODE HERE):
#     # YOUR CODE HERE

import subprocess
import json
import web3
import bit
import os
from dotenv import load_dotenv
load_dotenv()

# for BITTEST
from bit import PrivateKeyTestnet
from bit.network import NetworkAPI


from constants import BTC, BTCTEST, ETH
#from constants import *

# for ETH
from web3 import Web3
from eth_account import Account
from pathlib import Path
from getpass import getpass


# Ganache local host (http://127.0.0.1:8545) object
from web3 import Account
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

from web3.gas_strategies.time_based import medium_gas_price_strategy
w3.eth.setGasPriceStrategy(medium_gas_price_strategy)

# Support the PoA algorithm
from web3.middleware import geth_poa_middleware
w3.middleware_onion.inject(geth_poa_middleware, layer=0)



# Set the 12 word mnemonic as an environment variable, and include the one you generated as a fallback
mnemonic = os.getenv('MNEMONIC', 'punch wife raw spirit comfort inspire bean shuffle cheese dutch around wedding')

# Create function to get the BIP44-derived wallet addresses 
# I created a symlink called derive for the hd-wallet-derive/hd-wallet-derive.php in advance

def derive_wallets(coin, mnemonic, numderive=3):
    command = f'php derive -g --coin={coin} --format=json --numderive={numderive} --mnemonic="{mnemonic}"'

    p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    p_status = p.wait()

    return json.loads(output)

# Create an object called coins that derives ETH and BTCTEST wallets with the derive_wallets function.

coin_type = [BTC, ETH, BTCTEST]
coins = {}
for x in coin_type:
    coins[x] = derive_wallets(x, mnemonic)


def privateKeyToAccount(coin, priv_key):
    if coin==ETH:
        return Account.privateKeyToAccount(priv_key)

    elif coin==BTCTEST:
        return PrivateKeyTestnet(priv_key)


def create_raw_tx(coin, account, to, amount):
    if coin==ETH:
        gasEstimate = w3.eth.estimateGas(
            {"from": account.address, "to": to, "value": amount}
        )
        return {
            "from": account.address,
            "to": to,
            "value": amount,
            "gasPrice": w3.eth.gasPrice,
            "gas": gasEstimate,
            "nonce": w3.eth.getTransactionCount(account.address),
            "chainId": w3.eth.chain_id
        }
    elif coin==BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, BTC)])

def send_tx(coin, account, to, amount):
    raw_tx = create_raw_tx(coin, account, to, amount)
    signed = account.sign_transaction(raw_tx)
    if coin==ETH:
        results = w3.eth.sendRawTransaction(signed.rawTransaction)
        print(results.hex())
        return results.hex()
    elif coin==BTCTEST:        
        results = NetworkAPI.broadcast_tx_testnet(signed)
        return results