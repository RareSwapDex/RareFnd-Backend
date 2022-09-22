from pprint import pprint
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets
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
)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django_email_verification import send_email
import traceback
from django.contrib.auth import get_user_model
import smtplib
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required


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
        queryset = Project.objects.all()
        serializer = ProjectSerializer(queryset, many=True)
        print(serializer.data)
        return Response({"projects": serializer.data})


@api_view(["GET", "PUT"])
def projects_details(request, id):
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


@api_view(["POST"])
@login_required
def add_project(request):
    if request.method == "POST":
        print("************************", request.user)
        print(request.headers)
        pprint(request.data)

        project = Project(owner=request.user, projectData=request.data)
        project.clean()
        project.save()
        return Response(status=status.HTTP_201_CREATED)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(status=status.HTTP_201_CREATED)
        # print(serializer.errors)

        # project_data = {
        #     "title": request.data["basics"]["projectTitle"] or None,
        #     "head": request.data["basics"]["projectHead"] or None,
        #     "country": request.data["basics"]["projectCountry"] or None,
        #     "address": request.data["basics"]["projectAddress"] or None,
        #     "launch_date": request.data["projectLaunchDate"] or None,
        #     "deadline": request.data["projectDeadlineDate"] or None,
        #     "category": request.data["projectCategory"] or None,
        #     "subcategory": request.data["subcategory"] or None,
        #     "type": request.data["type"] or None,
        #     "fund_amount": request.data["fund_amount"] or None,
        #     "description": request.data["description"] or None,
        #     "company_name": request.data["company_name"] or None,
        #     "company_nature_of_business": request.data["company_nature_of_business"]
        #     or None,
        #     "company_address": request.data["company_address"] or None,
        #     "company_city": request.data["company_city"] or None,
        #     "company_zip_code": request.data["company_zip_code"] or None,
        #     "company_country": request.data["company_country"] or None,
        #     "company_incorporation_date": request.data["company_incorporation_date"]
        #     or None,
        #     "company_registration_number": request.data["company_registration_number"]
        #     or None,
        #     "company_estimated_annual_turnover": request.data[
        #         "company_estimated_annual_turnover"
        #     ]
        #     or None,
        #     "company_tax_country": request.data["title"] or None,
        #     "company_tax_identification_number": request.data["title"] or None,
        #     "company_white_paper_url": request.data["title"] or None,
        #     "company_tokenomics_url": request.data["title"] or None,
        #     "company_ubos": request.data["title"] or None,
        # }


@api_view(["GET"])
def countries_list(request):
    if request.method == "GET":
        queryset = Country.objects.all()
        serializer = CountrySerializer(queryset, many=True)
        return Response({"categories": serializer.data})


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
            projects = Project.objects.all()
        except Project.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        try:
            projects = Project.objects.filter(category__name=category_name)
        except Project.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        serializer = ProjectSerializer(projects, many=True)
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
        serializer = PendingContributionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        print(serializer.errors)


@api_view(["GET"])
def token_price(request):
    if request.method == "GET":
        queryset = TokenPrice.objects.all()[0]
        serializer = TokenPriceSerializer(queryset)
        return Response(serializer.data)


@api_view(["GET"])
def unique_username(request, field_to_check, field_value):
    if request.method == "GET":
        if field_to_check == "username":
            queryset = User.objects.filter(username__iexact=field_value)
            return Response({"valid": len(queryset) == 0})
        elif field_to_check == "email":
            queryset = User.objects.filter(email__iexact=field_value)
            return Response({"valid": len(queryset) == 0})


@api_view(["POST"])
def signup_user(request):
    if request.method == "POST":
        try:
            print(request.data)
            unverifiedUser = get_user_model().objects.create(
                username=request.data["username"],
                password=make_password(request.data["password"]),
                email=request.data["email"],
                first_name=request.data["first_name"],
                last_name=request.data["last_name"],
                phone=request.data["phone"],
                wallet_address=request.data["wallet_address"],
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

        # print(request.data)
        # serializer = UserSerializer(data=request.data)
        # if serializer.is_valid():
        #     serializer.save()
        #     send_email(request.data["username"])
        #     return Response(status=status.HTTP_200_OK)
        # print(serializer.errors)


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
