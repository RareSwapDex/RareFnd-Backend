from datetime import timedelta
import requests
from django.conf import settings
import urllib
from pprint import pprint
import os
import json
from .models import Project
import time
from web3 import Web3
from django.utils import timezone


# CLIENT_ID = settings.CLIENT_ID
# CLIENT_SECRET = settings.CLIENT_SECRET
CLIENT_ID = "TheRareAntiquities-capsule"
CLIENT_SECRET = "0d6aa5fe-97ea-40f9-b839-276240448758"
BNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
PIN_CODE = "4911"
# PIN_CODE = "9294"
AUTH_TOKEN = ""
AUTH_HEADERS = {}
with open(os.path.join(settings.STATIC_ROOT, "token.json")) as token_json:
    # with open("../static/token.json") as token_json:
    token_data = json.load(token_json)
    FND = token_data["token_address"]
    FND_ABI = token_data["token_abi"]
    FND_DECIMALS = token_data["token_decimals"]


def get_auth_token():
    global AUTH_TOKEN
    global AUTH_HEADERS
    details = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    response = requests.post(
        "https://login.arkane.network/auth/realms/Arkane/protocol/openid-connect/token",
        urllib.parse.urlencode(details),
        headers={"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"},
        timeout=10,
    ).json()
    pprint(response)
    AUTH_TOKEN = response["access_token"]
    AUTH_HEADERS = {"Authorization": f"Bearer {AUTH_TOKEN}"}


def get_wallet_by_identifier(identifier):
    get_auth_token()
    response = requests.get(
        f"https://api-wallet.venly.io/api/wallets?identifier={identifier}",
        headers=AUTH_HEADERS,
        timeout=60,
    ).json()
    return response["result"] if response["success"] else "Failed"


def get_wallet_by_address(address):
    get_auth_token()
    response = requests.get(
        f"https://api-wallet.venly.io/api/wallets?address={address}",
        headers=AUTH_HEADERS,
    ).json()
    # print(get_or_create_wallet(""))
    return response["result"][0] if response["success"] else "Failed"


def get_all_wallets():
    get_auth_token()
    response = requests.get(
        "https://api-wallet.venly.io/api/wallets", headers=AUTH_HEADERS
    ).json()
    return response["result"] if response["success"] else "Failed"


def create_wallet(identifier):
    get_auth_token()
    data = {
        "walletType": "WHITE_LABEL",
        "secretType": "BSC",
        "identifier": identifier,
        "pincode": "9294",
    }
    response = requests.post(
        "https://api-wallet.venly.io/api/wallets",
        json=data,
        headers=AUTH_HEADERS,
        timeout=10,
    ).json()
    return response["result"] if response["success"] else "failed"


def get_or_create_wallet(identifier):
    venly_wallet = get_wallet_by_identifier(identifier)
    if venly_wallet != "Failed":
        if len(venly_wallet) > 0:
            return venly_wallet[0]
        else:
            return create_wallet(identifier)


def get_BNB_balance(wallet):
    return wallet["balance"]["balance"]


def get_fnd_balance(wallet):
    get_auth_token()
    wallet_id = wallet["id"]
    response = requests.get(
        f"https://api-wallet.venly.io/api/wallets/{wallet_id}/balance/tokens/{FND}",
        headers=AUTH_HEADERS,
    ).json()
    if response["success"]:
        return response["result"]["balance"]
    else:
        return "Failed"


def get_swap_rates(bnb_to_swap):
    get_auth_token()
    response = requests.get(
        f"https://api-wallet.venly.io/api/swaps/rates?fromSecretType=BSC&toSecretType=BSC&fromToken=0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee&toToken={FND}&amount={bnb_to_swap}&orderType=SELL",
        headers=AUTH_HEADERS,
    ).json()
    return response


def swap_builder(wallet, pin_code, bnb_to_swap, fnd_to_receive):
    get_auth_token()
    wallet_id = wallet["id"]
    data = {
        # "enableGasEstimate": True,
        "pincode": pin_code,
        "walletId": wallet_id,
        "destinationWalletId": wallet_id,
        "fromSecretType": "BSC",
        "toSecretType": "BSC",
        "fromToken": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
        "toToken": FND,
        "inputAmount": bnb_to_swap,
        "outputAmount": fnd_to_receive,
        "orderType": "SELL",
        "exchange": "ONE_INCH",
    }
    response = requests.post(
        f"https://api-wallet.venly.io/api/wallets/{wallet_id}/swaps",
        json=data,
        headers=AUTH_HEADERS,
    ).json()
    print(response)
    return response["result"][0]


def execute_swap_transaction(wallet, pin_code, swap_builder, bnb_value_to_swap):
    get_auth_token()
    wallet_id = wallet["id"]
    data = {
        "walletId": wallet_id,
        "pincode": pin_code,
        "gasPrice": None,
        "gas": None,
        "value": Web3.toWei(bnb_value_to_swap, "ether"),
        "to": swap_builder["to"],
        "data": swap_builder["data"],
        "type": swap_builder["type"],
    }
    response = requests.post(
        f"https://api-wallet.venly.io/api/transactions/execute",
        json=data,
        headers=AUTH_HEADERS,
    ).json()
    return response


def approve_smart_contract(wallet, pin_code, sc_address):
    get_auth_token()
    wallet_id = wallet["id"]
    data = {
        "pincode": pin_code,
        "transactionRequest": {
            "type": "CONTRACT_EXECUTION",
            "walletId": wallet_id,
            "to": FND,
            "alias": None,
            "secretType": "BSC",
            "functionName": "approve",
            "value": 0,
            "inputs": [
                {
                    "type": "address",
                    "value": sc_address,
                },
                {"type": "uint256", "value": 2**256 - 1},
            ],
            "chainSpecificFields": {"gasLimit": "300000"},
        },
    }
    return requests.post(
        "https://api-wallet.venly.io/api/transactions/execute",
        json=data,
        headers=AUTH_HEADERS,
    ).json()


def stake(wallet, pin_code, sc_address, amount_to_stake):
    wallet_id = wallet["id"]
    data = {
        "pincode": pin_code,
        "transactionRequest": {
            "type": "CONTRACT_EXECUTION",
            "walletId": wallet_id,
            "to": sc_address,
            "alias": None,
            "secretType": "BSC",
            "functionName": "stake",
            "value": 0,
            "inputs": [
                {"type": "uint256", "value": Web3.toWei(amount_to_stake, "ether")},
            ],
            "chainSpecificFields": {"gasLimit": "300000"},
        },
    }
    return requests.post(
        "https://api-wallet.venly.io/api/transactions/execute",
        json=data,
        headers=AUTH_HEADERS,
    ).json()


def get_transaction_status(tx_status):
    get_auth_token()
    return requests.get(
        f"https://api-wallet.venly.io/api/transactions/BSC/{tx_status}/status",
        headers=AUTH_HEADERS,
    ).json()


def execute_stake(wallet_address, bnb_to_stake, project_id):
    # get_auth_token()
    pin_code = PIN_CODE
    sc_address = Project.objects.get(pk=project_id).staking_address
    wallet = get_wallet_by_address(wallet_address)
    bnb_to_stake = str(float(bnb_to_stake) - 0.003)
    swap_rates = get_swap_rates(bnb_to_stake)
    fnd_to_receive = swap_rates["result"]["bestRate"]["outputAmount"]
    swap_builder_response = swap_builder(wallet, pin_code, bnb_to_stake, fnd_to_receive)
    tx_hash = execute_swap_transaction(
        wallet, pin_code, swap_builder_response, bnb_to_stake
    )
    if not tx_hash["success"] and tx_hash["errors"][0]["code"] == "pincode.incorrect":
        pin_code = "9294"
        tx_hash = execute_swap_transaction(
            wallet, pin_code, swap_builder_response, bnb_to_stake
        )
    tx_hash = tx_hash["result"]["transactionHash"]
    while True:
        get_auth_token()
        tx = get_transaction_status(tx_hash)
        if tx["success"] == True:
            if tx["result"]["status"] == "SUCCEEDED":
                break
        else:
            time.sleep(2)
    tx_hash = approve_smart_contract(wallet, pin_code, sc_address)
    if not tx_hash["success"] and tx_hash["errors"][0]["code"] == "pincode.incorrect":
        pin_code = "9294"
        tx_hash = approve_smart_contract(wallet, pin_code, sc_address)
    tx_hash = tx_hash["result"]["transactionHash"]
    while True:
        get_auth_token()
        tx = get_transaction_status(tx_hash)
        if tx["success"] == True:
            if tx["result"]["status"] == "SUCCEEDED":
                break
        else:
            time.sleep(2)
    wallet_fnd_balance = get_fnd_balance(wallet) - 1
    tx_hash = stake(wallet, pin_code, sc_address, wallet_fnd_balance)
    tx_hash = tx_hash["result"]["transactionHash"]
    while True:
        get_auth_token()
        tx = get_transaction_status(tx_hash)
        if tx["success"] == True:
            if tx["result"]["status"] == "SUCCEEDED":
                return {
                    "hash": tx_hash,
                }
            else:
                time.sleep(2)


# get_auth_token()
# print(AUTH_HEADERS)
# wallet = get_or_create_wallet("jaliltest3@gmail.com")
# # wallet_fnd_balance = get_fnd_balance(wallet)
# # wallet_bnb_balance = get_BNB_balance(wallet)
# fnd_to_receive = get_swap_rates(0.001)["result"]["bestRate"]["outputAmount"]
# # pprint(fnd_to_receive)
# swap_builder_response = swap_builder(wallet, pin_code, 0.001, fnd_to_receive)
# # pprint(swap_builder_response)
# # exit()
# response = execute_transaction(wallet, PIN_CODE, swap_builder_response, 0.001 * 10**18)
# pprint(response)

# wallet_fnd_balance = get_fnd_balance(wallet)
# wallet_bnb_balance = get_BNB_balance(wallet)
# print(wallet_fnd_balance)
# print(wallet_bnb_balance)

# response = stake(
#     wallet, PIN_CODE, "0x1ABC0199f38f9BA14710957142e7924D3a2B24ff", 10 * 10**18
# )
# pprint(wallet)
# pprint(get_all_wallets())
