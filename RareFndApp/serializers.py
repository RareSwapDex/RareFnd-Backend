# import serializers from the REST framework
from rest_framework import serializers

# import the Project data model
from .models import (
    Country,
    Project,
    Category,
    Contribution,
    PendingContribution,
    Subcategory,
    TokenPrice,
    User,
    Incentive,
    RareFndData,
    EligibleCountry,
    RSVP,
)
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.hashers import make_password


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token["username"] = user.username
        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


# create a serializer class
class ProjectSerializer(serializers.ModelSerializer):
    number_of_subscribed_users = serializers.ReadOnlyField()
    owner_username = serializers.ReadOnlyField()
    number_of_donators = serializers.ReadOnlyField()
    owner_profile_picture = serializers.ReadOnlyField()

    # create a meta class
    class Meta:
        model = Project
        # fields = "__all__"
        fields = [
            "id",
            "owner",
            "owner_username",
            "owner_profile_picture",
            "title",
            "staking_address",
            "staking_abi",
            "head",
            "address",
            "thumbnail",
            "creation_datetime",
            "launch_date",
            "deadline",
            "fund_amount",
            "description",
            "company_name",
            "company_nature_of_business",
            # "company_white_paper_url",
            # "company_tokenomics_url",
            "raised_amount",
            "rewarded_amount",
            "current_reward",
            "approved",
            "live",
            "project_live_datetime",
            "country",
            "category",
            "subcategory",
            "type",
            "company_country",
            "number_of_subscribed_users",
            "number_of_donators",
            "featured",
            "recommended",
            "wallet_address",
            "currency",
            "ticket_price",
        ]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "arabic_name", "subheader", "arabic_subheader", "image"]


class ContributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contribution
        fields = [
            "id",
            "contributor_wallet_address",
            "project",
            "amount",
            "contribution_datetime",
            "hash",
        ]


class PendingContributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PendingContribution
        fields = ["id", "project", "hash"]


class TokenPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TokenPrice
        fields = ["price", "price_datetime"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "profile_picture",
            "email",
            "first_name",
            "last_name",
            "phone",
            "wallet_address",
            "bio",
        ]

    def validate_password(self, value: str) -> str:
        return make_password(value)


class IncentiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incentive
        fields = [
            "id",
            "title",
            "description",
            "included_incentives",
            "estimated_delivery",
            "available_items",
            "price",
            "reserved",
            "project",
            "display_order",
        ]


class IncentiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incentive
        fields = "__all__"


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = "__all__"


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = "__all__"


class RSVPSerializer(serializers.ModelSerializer):
    number_of_subscribers = serializers.ReadOnlyField()
    owner_username = serializers.ReadOnlyField()
    owner_profile_picture = serializers.ReadOnlyField()

    class Meta:
        model = RSVP
        fields = "__all__"


class EligibleCountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = EligibleCountry
        fields = "__all__"


class RareFndDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = RareFndData
        fields = "__all__"
