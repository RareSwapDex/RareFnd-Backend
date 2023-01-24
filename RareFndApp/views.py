from http.client import BAD_REQUEST
from pprint import pprint
from django.http import HttpResponse, JsonResponse
import json
from django.core.files.images import ImageFile, File
import io
from .serializers import (
    ProjectSerializer,
    CategorySerializer,
    ContributionSerializer,
    PendingContributionSerializer,
    TokenPriceSerializer,
    UserSerializer,
    IncentiveSerializer,
    SubCategorySerializer,
    CountrySerializer,
    RareFndDataSerializer,
    EligibleCountrySerializer,
)
from .models import (
    Project,
    Category,
    Contribution,
    PendingContribution,
    TokenPrice,
    User,
    Incentive,
    Subcategory,
    Country,
    RareFndData,
    ProjectFile,
    Type,
    EligibleCountry,
    MercuryoPendingStake,
)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django_email_verification import send_email
import traceback
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken, SlidingToken, UntypedToken
import boto3
from django.conf import settings
import urllib
import random
import string
import requests
from . import venly
from django.core.mail import send_mail
from coinbase_commerce.client import Client
from coinbase_commerce.webhook import Webhook
from coinbase_commerce.error import WebhookInvalidPayload, SignatureVerificationError
from decouple import config
import stripe
from .models_helper_functions import *
from .shopify_helper_functions import *


S3_BUCKET_KEY = settings.AWS_SECRET_ACCESS_KEY
S3_BUCKET_NAME = settings.AWS_STORAGE_BUCKET_NAME
CLIENT_ID = settings.CLIENT_ID
CLIENT_SECRET = settings.CLIENT_SECRET
RAREFND_URL = settings.RAREFND_URL
COINBASE_WEBHOOK_SECRET = config("COINBASE_WEBHOOK_SECRET")
COINBASE_API_KEY = config("COINBASE_API_KEY")
STRIPE_API_KEY = config("STRIPE_API_KEY")
STRIPE_WEBHOOK_SECRET = config("STRIPE_WEBHOOK_SECRET")
stripe.api_key = STRIPE_API_KEY


s3_session = boto3.Session(
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=S3_BUCKET_KEY,
)
s3 = s3_session.resource("s3")
bucket = s3.Bucket(S3_BUCKET_NAME)


# username='support@rarefnd.com'
# password='@Beastmode9294'
# mailserver = smtplib.SMTP('smtp.office365.com',587)
# mailserver.ehlo()
# mailserver.starttls()
# mailserver.login(username, password)
# #Adding a newline before the body text fixes the missing message body
# mailserver.sendmail('support@rarefnd.com','benharkatdjalil@gmail.com','\npython email')
# mailserver.quit()


# print("plplplplplplplpl")
# a = get_user_model().objects.create(
#     username="jaliloppl",
#     password="jalilrooney",
#     email="benharkatdjalil@gmail.com",
#     first_name="Abdeldjalil",
#     last_name="BENHARKAT",
#     phone="+213699752382",
#     wallet_address="0xCd3907Eb16A965445F91A75194A20C1E58127edd",
# )
# a.is_active = False
# print("k")
# try:
#     b = send_email(a)
# except:
#     print(traceback.format_exc())
# print("lllllllllll")
# print("qwqwqwwqwq", b)


def main(request):
    return HttpResponse("hello")


@api_view(["GET"])
def projects_list(request):
    if request.method == "GET":
        queryset = Project.objects.filter(approved=True)
        serializer = ProjectSerializer(queryset, many=True)
        return Response({"projects": serializer.data})


@api_view(["GET", "PUT"])
def projects_details_by_id(request, id):
    try:
        project = Project.objects.get(pk=id)
    except Project.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        serializer = ProjectSerializer(project)
        return Response(serializer.data)
    elif request.method == "PUT":
        serializer = ProjectSerializer(project, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        print(serializer.errors)
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT"])
def projects_details_by_title(request, title):
    try:
        project = Project.objects.filter(title__iexact=title)
        if len(project) <= 0:
            raise (Project.DoesNotExist)
        project = project[0]
    except Project.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        serializer = ProjectSerializer(project)
        return Response(serializer.data)
    elif request.method == "PUT":
        serializer = ProjectSerializer(project, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        print(serializer.errors)
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@login_required
def add_project(request):
    pprint(request.data)
    if request.method == "POST":
        try:
            project = Project(
                owner=request.user,
                title=request.data.get("basics.projectTitle"),
                head=request.data.get("basics.projectHead"),
                country_id=EligibleCountry.objects.get(
                    nicename=request.data.get("basics.projectCountry")
                ).id,
                address=request.data.get("basics.projectAddress"),
                thumbnail=ImageFile(
                    io.BytesIO(request.data.get("basics.projectImageFile").read()),
                    name="thumbnail.jpg",
                ),
                launch_date=request.data.get("basics.projectLaunchDate"),
                deadline=request.data.get("basics.projectDeadlineDate"),
                category_id=Category.objects.get(
                    name=request.data.get("basics.projectCategory")
                ).id
                if request.data.get("basics.projectCategory")
                else None,
                subcategory_id=Subcategory.objects.get(
                    name=request.data.get("basics.projectSubcategory")
                ).id
                if request.data.get("basics.projectSubcategory")
                else None,
                type_id=Type.objects.get(
                    name=request.data.get("basics.projectType")
                ).id,
                fund_amount=request.data.get("funding.projectFundsAmount"),
                description=request.data.get("story.projectStory"),
                company_name=request.data.get("payment.companyName"),
                company_nature_of_business=request.data.get("payment.natureOfBusiness"),
                company_address=request.data.get("payment.companyAddress"),
                company_city=request.data.get("payment.companyCity"),
                company_zip_code=request.data.get("payment.companyZipCode"),
                company_country_id=EligibleCountry.objects.get(
                    nicename=request.data.get("payment.companyCountry")
                ).id,
                company_incorporation_date=request.data.get(
                    "payment.projectIncorporationDate"
                ),
                company_registration_number=request.data.get(
                    "payment.companyRegistrationNumber"
                ),
                company_estimated_annual_turnover=request.data.get(
                    "payment.companyEstimatedAnnualTurnover"
                ),
                company_tax_country_id=EligibleCountry.objects.get(
                    nicename=request.data.get("payment.projectTaxCountry")
                ).id,
                company_tax_identification_number=request.data.get(
                    "payment.taxIdNumber"
                ),
                wallet_address=request.data.get("payment.ownerWalletAddress"),
                # company_white_paper_url=request.data.get("payment.whitePaperUrl"),
                # company_tokenomics_url=request.data.get("payment.tokenomicsUrl"),
                # company_ubos=[
                #     {ubo_data: request.data[ubo_data]}
                #     for ubo_data in request.data
                #     if ubo_data.startswith("payment.UBOs") and "File" not in ubo_data
                # ],
            )
            project.clean()
            project.save()
            rewards_dict = {}
            for key in request.data.keys():
                if key.startswith("rewards."):
                    if key.split(".")[1] not in rewards_dict:
                        rewards_dict[key.split(".")[1]] = {}
                    if key.split(".")[2] == "incentives":
                        if "incentives" not in rewards_dict[key.split(".")[1]]:
                            rewards_dict[key.split(".")[1]]["incentives"] = {}
                        rewards_dict[key.split(".")[1]]["incentives"][
                            key.split(".")[3]
                        ] = request.data[key]
                    else:
                        rewards_dict[key.split(".")[1]][
                            key.split(".")[2]
                        ] = request.data[key]
            for reward in rewards_dict:
                incentive = Incentive(
                    title=rewards_dict[reward].get("incentiveTitle"),
                    description=rewards_dict[reward].get("incentiveDescription"),
                    included_incentives=list(
                        rewards_dict[reward].get("incentives").values()
                    )
                    if rewards_dict[reward].get("incentives")
                    else [],
                    estimated_delivery=rewards_dict[reward].get(
                        "incentiveEstimatedDelivery"
                    ),
                    available_items=int(
                        rewards_dict[reward].get("availableIncentives")
                    ),
                    price=float(rewards_dict[reward].get("incentivePrice")),
                    project=project,
                )
                incentive.clean()
                incentive.save()
            for key in request.FILES.keys():
                if request.FILES.get(key) and key != "basics.projectImageFile":
                    file = ProjectFile(
                        owner=project,
                        file=File(
                            io.BytesIO(request.FILES.get(key).read()),
                            name=request.FILES.get(key).__str__(),
                        ),
                    )
                    file.save()
            return Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            print(traceback.format_exc())
            return Response({"errors": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@login_required
def subscribe_to_project(request):
    try:
        project = Project.objects.get(pk=request.data["projectId"])
        if request.user not in project.subscribed_users.all():
            project.subscribed_users.add(request.user)
        return Response(status=status.HTTP_200_OK)
    except Exception:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
@login_required
def upload_ckeditor_image(request):
    try:
        file_extension = str(request.data["ckeditorFile"]).split(".")[-1]
        gen_file_name = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=10)
        )
        path = f"projects/CKEditor/{gen_file_name}.{file_extension}"
        s3_obj = bucket.Object(path)
        s3_obj.put(ACL="public-read")
        s3_obj.upload_fileobj(
            # request.data["ckeditorFile"].file, ExtraArgs={"ACL": "public-read"}
            request.data["ckeditorFile"].file,
        )
        return Response(
            {"url": f"https://rarefnd-bucket.s3.us-east-2.amazonaws.com/{path}"},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        print(traceback.format_exc())
        return Response({"response": e}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@login_required
def check_subscribed_to_project(request, projectId):
    try:
        project = Project.objects.get(pk=projectId)
        return Response(
            {"subscribed": request.user in project.subscribed_users.all()},
            status=status.HTTP_200_OK,
        )
    except Exception:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
@login_required
def get_profile_info(request):
    if request.user.is_authenticated:
        queryset = User.objects.get(username=request.user.username)
        serializer = UserSerializer(queryset)
        return Response(serializer.data)
    return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
def countries_list(request):
    if request.method == "GET":
        queryset = Country.objects.all()
        serializer = CountrySerializer(queryset, many=True)
        return Response({"countries": serializer.data})


@api_view(["GET"])
def eligible_countries_list(request):
    if request.method == "GET":
        queryset = EligibleCountry.objects.all()
        serializer = EligibleCountrySerializer(queryset, many=True)
        return Response({"eligible_countries": serializer.data})


@api_view(["GET"])
def categories_list(request):
    if request.method == "GET":
        queryset = Category.objects.all()
        serializer = CategorySerializer(queryset, many=True)
        return Response({"categories": serializer.data})


@api_view(["GET"])
def subcategories_list_of_category(request, category_name):
    if request.method == "GET":
        queryset = Subcategory.objects.filter(category__name__iexact=category_name)
        serializer = SubCategorySerializer(queryset, many=True)
        return Response({"subcategories": serializer.data})


@api_view(["GET"])
def projects_from_category(request, category_name):
    if category_name == "all":
        try:
            projects = Project.objects.filter(approved=True)
        except Project.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        try:
            projects = Project.objects.filter(
                category__name=category_name, approved=True
            )
        except Project.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        serializer = ProjectSerializer(projects, many=True)
        pprint(serializer.data)
        return Response({"projects": serializer.data})


@api_view(["GET"])
def contributions_list(request):
    if request.method == "GET":
        queryset = Contribution.objects.all()
        serializer = ContributionSerializer(queryset, many=True)
        return Response({"contributions": serializer.data})


@api_view(["GET", "POST"])
def pending_contributions_list(request):
    if request.method == "GET":
        queryset = PendingContribution.objects.all()
        serializer = PendingContributionSerializer(queryset, many=True)
        return Response({"pending_contributions": serializer.data})
    elif request.method == "POST":
        p_c = PendingContribution(
            hash=request.data["hash"],
            project=Project.objects.get(pk=request.data["project"]),
            selected_incentive=Incentive.objects.get(
                pk=request.data["selected_incentive"]
            ),
        )
        p_c.save()
        return Response(status=status.HTTP_201_CREATED)


@api_view(["GET"])
def token_price(request):
    if request.method == "GET":
        queryset = TokenPrice.objects.all()[0]
        serializer = TokenPriceSerializer(queryset)
        return Response(serializer.data)


@api_view(["GET"])
def unique_record(request, field_to_check, field_value):
    if request.method == "GET":
        if field_to_check == "username":
            if request.user.is_authenticated and request.user.username == field_value:
                return Response({"valid": True})
            queryset = User.objects.filter(username__iexact=field_value)
            return Response({"valid": len(queryset) == 0})
        elif field_to_check == "email":
            if request.user.is_authenticated and request.user.email == field_value:
                return Response({"valid": True})
            queryset = User.objects.filter(email__iexact=field_value)
            return Response({"valid": len(queryset) == 0})
        elif field_to_check == "project_title":
            queryset = Project.objects.filter(title__iexact=field_value)
            return Response({"valid": len(queryset) == 0})


@api_view(["POST"])
def signup_user(request):
    if request.method == "POST":
        try:
            pprint(request.data)
            unverifiedUser = get_user_model().objects.create(
                username=request.data["username"],
                password=make_password(request.data["password"]),
                email=request.data["email"],
                first_name=request.data.get("first_name"),
                last_name=request.data.get("last_name"),
                phone=request.data.get("phone"),
                wallet_address=request.data.get("wallet_address"),
            )
            unverifiedUser.is_active = False
            try:
                send_email(unverifiedUser)
                return Response(status=status.HTTP_200_OK)
            except Exception:
                print(traceback.format_exc())
                return Response({"errors": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(traceback.format_exc())
            return Response({"errors": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@login_required
def update_user(request):
    try:
        user = User.objects.get(pk=request.user.id)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    data = request.data
    if data.get("profile_picture.0") and type(data.get("profile_picture.0")) != str:
        data["profile_picture"] = File(
            io.BytesIO(data["profile_picture.0"].read()),
            name=data["profile_picture.0"].__str__(),
        )
    serializer = UserSerializer(user, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    print(serializer.errors)
    return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def incentives(request, project_id):
    if request.method == "GET":
        queryset = Incentive.objects.filter(project__id=project_id)
        serializer = IncentiveSerializer(queryset, many=True)
        return Response({"incentives": serializer.data}, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_rare_fnd_data(request):
    if request.method == "GET":
        queryset = RareFndData.objects.all()[0]
        serializer = RareFndDataSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def user_info(request, user_id):
    if request.method == "GET":
        queryset = User.objects.get(pk=user_id)
        serializer = UserSerializer(queryset)
        tmp = serializer.data
        del tmp["phone"]
        del tmp["wallet_address"]
        return Response(tmp, status=status.HTTP_200_OK)


def get_venly_auth_helper():
    details = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    response = requests.post(
        # "https://login-staging.arkane.network/auth/realms/Arkane/protocol/openid-connect/token",
        "https://login.arkane.network/auth/realms/Arkane/protocol/openid-connect/token",
        urllib.parse.urlencode(details),
        headers={"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"},
    ).json()
    return response


@api_view(["GET"])
def get_venly_auth(request):
    if request.method == "GET":
        response = get_venly_auth_helper()
        return Response(response, status=status.HTTP_200_OK)


@api_view(["POST"])
def venly_execute_swap(request):
    data = request.data
    access_token = data["token"]
    del data["token"]
    response = requests.post(
        "https://api-wallet.venly.io/api/transactions/execute",
        json=data,
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )
    return Response(response, status=status.HTTP_200_OK)


@api_view(["GET"])
def venly_create_wallet(request, email, usd_amount, smart_contract_address, project_id):
    wallet = venly.get_or_create_wallet(email)
    if wallet.get("address"):
        pending_stake = MercuryoPendingStake(
            wallet_address=wallet.get("address"),
            smart_contract_address=smart_contract_address,
            usd_amount=usd_amount,
            project_id=project_id,
        )
        pending_stake.clean()
        pending_stake.save()
        response = {"address": wallet.get("address")}
        return Response(response, status=status.HTTP_200_OK)


@api_view(["POST"])
def mercuryo_callback_wallet_received_bnb(request):
    # wallet = venly.get_or_create_wallet()
    # response = {"address": wallet.get("address"), "email": wallet.get("identifier")}
    pprint(request.data)
    if request.data.get("payload"):
        data = request.data["payload"]["data"]
    else:
        data = request.data["data"]

    if data["status"] == "completed":
        usd_amount_to_stake = data["fiat_amount"]
        bnb_to_stake = data["amount"]
        wallet_address = data["tx"]["address"]
        MercuryoPendingStake.objects.filter(
            wallet_address=wallet_address, usd_amount=usd_amount_to_stake
        ).update(bnb_amount=bnb_to_stake)
        response = venly.execute_stake(
            wallet_address, usd_amount_to_stake, bnb_to_stake
        )
        if response is None:
            return Response(
                {
                    "NOT STAKED": "Could NOT stake: 'venly.execute_stake' function returned None, this means that there is no pending contribution found with less than 4 hours 'threshold', otherwise something wrong wend with the staking operation"
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = PendingContributionSerializer(data=response)
        if serializer.is_valid():
            serializer.save()
        MercuryoPendingStake.objects.filter(
            staking_transaction_hash=response["hash"]
        ).delete()
    # return Response(response, status=status.HTTP_200_OK)
    return Response(
        {
            "OK": f"Address {wallet_address} staked {bnb_to_stake}BNB to project id {response['project']}, tx hash: {response['hash']}"
        },
        status=status.HTTP_200_OK,
    )


def backend_send_email(subject, message, email_from, recipient_list):
    subject = subject
    message = message
    email_from = email_from
    recipient_list = recipient_list
    send_mail(subject, message, email_from, recipient_list)


@api_view(["POST"])
def user_reset_password(request):
    email = request.data["email"]
    # Check if email exists in our database
    user = User.objects.filter(email=email)
    if not user:
        return Response(status=status.HTTP_200_OK)
    # add token to password_reset_token User field
    token = "".join(random.choices(string.ascii_uppercase + string.digits, k=254))
    reset_password_email_link = (
        f"https://rarefnd.com/user/reset_password/{email}/{token}"
    )
    User.objects.filter(email=email).update(password_reset_token=token)
    backend_send_email(
        subject="RareFnd: Reset password",
        message=f"Please click on the link bellow to reset your password\n{reset_password_email_link}",
        email_from=settings.EMAIL_HOST_USER,
        recipient_list=[
            email,
        ],
    )
    return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
def check_reset_password_token(request):
    email = request.data["email"]
    token = request.data["token"]
    user = User.objects.filter(email=email)
    if not user:
        return Response(status=status.HTTP_403_FORBIDDEN)
    user = user[0]
    user_token = user.password_reset_token
    if token != user_token or token == "" or token is None:
        return Response(status=status.HTTP_403_FORBIDDEN)
    return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
def user_change_password(request):
    email = request.data["email"]
    password = request.data["password"]
    token = request.data["token"]
    user = User.objects.filter(email=email)
    if not user:
        return Response(status=status.HTTP_403_FORBIDDEN)
    user = user[0]
    user_token = user.password_reset_token
    if token != user_token or token == "" or token is None:
        return Response(status=status.HTTP_403_FORBIDDEN)
    user.set_password(password)
    user.save()
    new_token = "".join(random.choices(string.ascii_uppercase + string.digits, k=254))
    User.objects.filter(email=email).update(password_reset_token=new_token)
    return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
def coinbase_create_charge(request):
    client = Client(api_key=COINBASE_API_KEY)
    project_name = request.data.get("projectName")
    contributor_email = request.data.get("contributorEmail")
    project_contract_address = request.data.get("projectContractAddress")
    contribution_amount = request.data.get("contributionAmount")
    project_id = request.data.get("projectId")
    project_url = request.data.get("projectURL")
    selected_incentive = request.data.get("selected_incentive")
    contribution = {
        "name": project_name,
        "local_price": {"amount": contribution_amount, "currency": "USD"},
        "pricing_type": "fixed_price",
        "redirect_url": f"{project_url}?payment_status=success",
        "cancel_url": f"{project_url}?payment_status=failed",
        "metadata": {
            "contributor_email": contributor_email,
            "project_contract_address": project_contract_address,
            "project_id": project_id,
            "selected_incentive": selected_incentive,
        },
    }
    charge = client.charge.create(**contribution)
    return Response({"message": "success", "data": charge}, status=status.HTTP_200_OK)


@api_view(["POST"])
def coinbase_webhook(request):
    # request_data = json.dumps(request.data)
    request_data = request.body.decode("utf-8")
    request_sig = request.headers.get("X-CC-Webhook-Signature", None)
    try:
        # signature verification and event object construction
        event = Webhook.construct_event(
            request_data, request_sig, COINBASE_WEBHOOK_SECRET
        )
    except (WebhookInvalidPayload, SignatureVerificationError) as e:
        print(e)
        return Response({"message": f"{str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    if event["type"] == "charge:confirmed":
        project_id = int(event["data"]["metadata"]["project_id"])
        selected_incentive = int(event["data"]["metadata"]["selected_incentive"])
        contributor_email = event["data"]["metadata"]["contributor_email"]
        contribution_amount = float(
            event["data"]["payments"][0]["net"]["local"]["amount"]
        )
        contribution_hash = event["data"]["payments"][0]["transaction_id"]
        # Add contribution to "Contribution" table
        add_contribution_to_contribution_table(
            "0",
            contributor_email,
            project_id,
            contribution_amount,
            "coinbase",
            contribution_hash,
            selected_incentive,
        )
        # # Add amount to project rased_amount
        # add_amount_to_project_raised_amount(project_id, contribution_amount)
        # # Check if project reached target amount
        # check_project_reached_target(project_id)
    return Response({"message": "success"}, status=status.HTTP_200_OK)


@api_view(["POST"])
def stripe_create_charge(request):
    project_name = request.data.get("projectName")
    contributor_email = request.data.get("contributorEmail")
    project_contract_address = request.data.get("projectContractAddress")
    contribution_amount = request.data.get("contributionAmount")
    project_id = request.data.get("projectId")
    project_url = request.data.get("projectURL")
    selected_incentive = request.data.get("selectedIncentive")
    # Create a product
    product = stripe.Product.create(
        name=project_name,
        default_price_data={
            "currency": "usd",
            "unit_amount_decimal": float(contribution_amount) * 100,
        },
        metadata={
            "name": project_name,
            "contributor_email": contributor_email,
            "project_contract_address": project_contract_address,
            "project_id": project_id,
            "selected_incentive": selected_incentive,
        },
    )
    pprint(product)
    price_id = product["default_price"]
    # Create checkout for the price_id
    checkout = stripe.checkout.Session.create(
        success_url=f"{project_url}?payment_status=success",
        cancel_url=f"{project_url}?payment_status=failed",
        customer_email=contributor_email,
        line_items=[
            {
                "price": price_id,
                "quantity": 1,
            },
        ],
        mode="payment",
        metadata={
            "contributor_email": contributor_email,
            "project_contract_address": project_contract_address,
            "project_id": project_id,
            "selected_incentive": selected_incentive,
        },
    )
    return Response(
        {"message": "success", "hosted_url": checkout["url"]}, status=status.HTTP_200_OK
    )


@api_view(["POST"])
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
    # check payment success
    if event.type == "payment_intent.succeeded":
        payment_intent = event.data.object  # contains a stripe.PaymentIntent
        payment_intent_id = payment_intent["id"]
        # Get checkout session related to this id
        c_s = stripe.checkout.Session.list(payment_intent=payment_intent_id)
        # Add contribution to "Contribution" table
        project_id = c_s["data"][0]["metadata"]["project_id"]
        contributor_email = c_s["data"][0]["metadata"]["contributor_email"]
        contribution_amount = float(payment_intent["amount_received"] / 100)
        selected_incentive = c_s["data"][0]["metadata"]["selected_incentive"]
        add_contribution_to_contribution_table(
            "0",
            contributor_email,
            project_id,
            contribution_amount,
            "stripe",
            "0",
            selected_incentive,
        )
        # # Add amount to project rased_amount
        # add_amount_to_project_raised_amount(project_id, contribution_amount)
        # # Check if project reached target amount
        # check_project_reached_target(project_id)
        return Response({"message": "success"}, status=status.HTTP_200_OK)
    return HttpResponse(status=200)


@api_view(["POST"])
def shopify_create_checkout(request):
    project_name = request.data.get("projectName")
    contributor_email = request.data.get("contributorEmail")
    project_contract_address = request.data.get("projectContractAddress")
    contribution_amount = request.data.get("contributionAmount")
    project_id = request.data.get("projectId")
    project_url = request.data.get("projectURL")
    # Create a product
    product = shopify_create_product(
        project_name,
        contribution_amount,
        contributor_email,
        project_contract_address,
        project_id,
    )
    if not product["success"]:
        return Response(
            {"message": "failed", "data": "failed to create a checkout"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    pprint(product)
    variant_id = product["variant_id"]
    # Create checkout for the price_id
    checkout = create_checkout(
        variant_id,
        contributor_email,
        f"{project_url}?payment_status=success",
        f"{project_url}?payment_status=failed",
    )
    return (
        Response(
            {"message": "success", "data": checkout["web_url"]},
            status=status.HTTP_200_OK,
        )
        if checkout["success"]
        else Response(
            {
                "message": "failed",
                "data": "created product but failed to create a checkout",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    )
