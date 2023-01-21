from pprint import pprint
from web3 import Web3
import requests


web3 = Web3()


def get_transaction_chain(tx_hash):
    r = requests.get(tx_hash)
    location = r.headers.get("Onion-Location")
    return location.split("/")[3].split("/")[0] if location else None


def get_transactions_details(tx_hash):
    a = web3.eth.getTransaction(tx_hash)
    chain = get_transaction_chain(tx_hash)
    pprint(a)
