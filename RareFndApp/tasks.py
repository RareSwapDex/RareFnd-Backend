import time
from .serializers import PendingContributionSerializer
from .models import PendingContribution, Contribution, Project, TokenPrice, Incentive
from collections import OrderedDict
from web3 import Web3
import traceback
from pprint import pprint
import json
from eth_defi.abi import get_deployed_contract
from web3.middleware import geth_poa_middleware
from datetime import datetime
from django.templatetags.static import static
import os
from django.conf import settings


web3 = Web3(Web3.HTTPProvider("https://bsc-dataseed.binance.org/"))
web3.middleware_onion.inject(geth_poa_middleware, layer=0)
router_pancake_swap = "0x10ED43C718714eb63d5aA57B78B54704E256024E"

# with open("./static/token.json") as token_json:
with open(os.path.join(settings.STATIC_ROOT, "token.json")) as token_json:
    token_data = json.load(token_json)
    FND = token_data["token_address"]
    FND_ABI = token_data["token_abi"]
    FND_DECIMALS = token_data["token_decimals"]
BNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
BUSD = "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56"
FND_BNB = "0x076b01af4949898303f364c4308aa4F9Ce010dC8"
FND_USD_PRICE = 0


def start_tasks():
    while True:
        try:
            check_pending_contributions()
        except Exception:
            print(traceback.format_exc())
        try:
            update_project_rewards()
        except Exception:
            print(traceback.format_exc())
        # try:
        #     get_fnd_usd_value(FND, BNB, BUSD, FND_BNB, router_pancake_swap)
        # except Exception:
        #     print(traceback.format_exc())
        time.sleep(5)


def update_project_rewards():
    live_projects = Project.objects.filter(live=True)
    for project in live_projects:
        project_contributions = Contribution.objects.filter(project=project)
        project_reward = 0
        for contribution in project_contributions:
            # time_since_contribution in seconds
            time_since_contribution = (
                datetime.now() - contribution.contribution_datetime.replace(tzinfo=None)
            ).total_seconds()

            contribution_amount = contribution.amount
            project_reward += (
                contribution_amount * (2.4 / 31536000) * time_since_contribution
            )
        project.current_reward = round(project_reward, 2)
        project.save()


def decode_transaction_input(tx_input, staking_address, staking_abi):
    contract = web3.eth.contract(address=staking_address, abi=staking_abi)
    decoded_input = contract.decode_function_input(tx_input)
    return decoded_input


def check_pending_contributions():
    queryset = PendingContribution.objects.all()
    serializer = PendingContributionSerializer(queryset, many=True)
    pending_contributions = serializer.data
    for p in pending_contributions:
        tx = dict(OrderedDict(p))
        selected_incentive = PendingContribution.objects.get(
            pk=tx["id"]
        ).selected_incentive

        # Test if Tx hash already in Contribution table
        if Contribution.objects.filter(hash__iexact=tx["hash"]):
            PendingContribution.objects.filter(hash=tx["hash"]).delete()
            continue
        receipt = {}
        try:
            receipt = dict(web3.eth.wait_for_transaction_receipt(tx["hash"], timeout=5))
        except Exception:
            continue
        # Test if tx is success and the token sent is FND
        if (
            receipt
            and receipt["status"]
            and receipt["logs"]
            and receipt["logs"][0]["address"].lower() == FND.lower()
        ):
            web3_tx = web3.eth.get_transaction(tx["hash"])
            tx_input = web3_tx["input"]
            tx_block_number = web3_tx["blockNumber"]
            tx_project = Project.objects.get(pk=tx["project"])
            tx_project_staking_address = getattr(tx_project, "staking_address")
            tx_project_staking_abi = json.loads(getattr(tx_project, "staking_abi"))
            decoded_tx = decode_transaction_input(
                tx_input, tx_project_staking_address, tx_project_staking_abi
            )
            # tx_recipient = decoded_tx[1]['recipient']
            tx_recipient = receipt["to"]
            # tx_amount in usd
            try:
                tx_amount = decoded_tx[1]["usdAmount"] / 1000000000000000000
            except KeyError:
                if decoded_tx[1]["stakeAmount"]:
                    tx_amount = (
                        decoded_tx[1]["stakeAmount"] / 1000000000000000000
                    ) * get_fnd_usd_value(FND, BNB, BUSD, FND_BNB, router_pancake_swap)[
                        "fnd_usd"
                    ]
            tx_timestamp = web3.eth.get_block(tx_block_number)["timestamp"]
            tx_project_live = getattr(tx_project, "live")
            tx_project_live_datetime = getattr(
                tx_project, "project_live_datetime"
            ).replace(tzinfo=None)
            """
            Next we check if:
            1- Project is live
            3- Tx recipient wallet is the same project address
            4- Contribution time is after project went live
            """
            if (
                tx_project_live
                and (tx_project_staking_address.lower() == tx_recipient.lower())
                and datetime.fromtimestamp(tx_timestamp) > tx_project_live_datetime
            ):
                # Add to contributions table
                contribution = Contribution(
                    contributor_wallet_address=receipt["from"].lower(),
                    project=tx_project,
                    amount=tx_amount,
                    hash=tx["hash"],
                    selected_incentive=selected_incentive
                    if selected_incentive.available_items > 0
                    else None,
                    eligible_for_selected_incentive=tx_amount
                    >= selected_incentive.price
                    if selected_incentive and selected_incentive.available_items > 0
                    else False,
                )
                contribution.save()
                if (
                    selected_incentive != None
                    and tx_amount >= selected_incentive.price
                    and selected_incentive.available_items > 0
                ):
                    Incentive.objects.filter(id=int(selected_incentive.id)).update(
                        available_items=selected_incentive.available_items - 1
                    )

                # Add amount to project raised_amount
                project_raised_amount = getattr(tx_project, "raised_amount")
                Project.objects.filter(pk=tx["project"]).update(
                    raised_amount=project_raised_amount + tx_amount
                )
                tx_project = Project.objects.get(pk=tx["project"])
                # Remove pending contribution from the table
                PendingContribution.objects.filter(hash=tx["hash"]).delete()
                # Check if project reached target amount
                # tx_project_fund_amount = getattr(tx_project, "fund_amount")
                # tx_project_raised_amount = getattr(tx_project, "raised_amount")
                # tx_project_current_reward = getattr(tx_project, "current_reward")
                # # print(
                # #     tx_project_raised_amount + tx_project_current_reward,
                # #     tx_project_fund_amount,
                # #     (tx_project_raised_amount + tx_project_current_reward)
                # #     >= tx_project_fund_amount,
                # # )
                # if (
                #     tx_project_raised_amount + tx_project_current_reward
                # ) >= tx_project_fund_amount:
                #     Project.objects.filter(pk=tx["project"]).update(live=False)


def get_bnb_usd_value(bnb_address, busd_address, router_pancake_swap):
    routerContract = web3.eth.contract(
        address=router_pancake_swap,
        # abi=json.load(open("./static/pancake_swap_abi.json")),
        abi=json.load(
            open(os.path.join(settings.STATIC_ROOT, "pancake_swap_abi.json"))
        ),
    )
    oneToken = web3.toWei(1, "Ether")
    price = routerContract.functions.getAmountsOut(
        oneToken, [bnb_address, busd_address]
    ).call()
    normalizedPrice = web3.fromWei(price[1], "Ether")
    return normalizedPrice


def get_fnd_usd_value(
    fnd_address, bnb_address, busd_address, fnd_bnb, router_pancake_swap
):
    global FND_USD_PRICE
    pair = get_deployed_contract(web3, "UniswapV2Pair.json", fnd_bnb)
    FND_liquidity, BNB_liquidity, timestamp = pair.functions.getReserves().call()
    bnb_usd_value = float(
        get_bnb_usd_value(bnb_address, busd_address, router_pancake_swap)
    )
    fnd_bnb_value = float(BNB_liquidity) / float(FND_liquidity)
    fnd_usd_value = fnd_bnb_value * bnb_usd_value
    # token_price = TokenPrice.objects.filter()
    # if token_price:
    #     token_price[0].price = fnd_usd_value
    #     token_price[0].save()
    # else:
    #     t_p = TokenPrice(price=fnd_usd_value)
    #     t_p.save()
    FND_USD_PRICE = fnd_usd_value
    return {"fnd_usd": fnd_usd_value, "timestamp": timestamp}
