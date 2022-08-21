
# import serializers from the REST framework
from rest_framework import serializers
 
# import the Project data model
from .models import Project, Category, Contribution, PendingContribution, TokenPrice, User, Incentive
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        # ...

        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

# create a serializer class
class ProjectSerializer(serializers.ModelSerializer):
    # create a meta class
    class Meta:
        model = Project
        fields = ['id', 'owner', 'title', 'head', 'description', 'thumbnail', 'description', 'type', 'category', 'subcategory', 'country', 'address', 'creation_datetime', 'fund_amount', 'raised_amount', 'rewarded_amount', 'staking_address', 'staking_abi', 'deadline', 'aproved', 'live']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'image']


class ContributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contribution
        fields = ['id', 'contributor_wallet_address', 'project', 'amount', 'contribution_datetime', 'hash']
        
        
class PendingContributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PendingContribution
        fields = ['id', 'project', 'hash']
        
class TokenPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TokenPrice
        fields = ['price', 'price_datetime']
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'phone', 'wallet_address']
        
        
class IncentiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incentive
        fields = ['id', 'title', 'description', 'included_incentives', 
                  'estimated_delivery', 'available_items', 'price', 
                  'reserved', 'project']
        
