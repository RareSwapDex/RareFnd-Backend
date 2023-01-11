from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from ckeditor.fields import RichTextField
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.core.validators import FileExtensionValidator
from django.db.models import JSONField
import datetime as dt


class UserManager(BaseUserManager):
    def create_user(
        self,
        email,
        username,
        bio,
        password,
        first_name=None,
        last_name=None,
        profile_picture=None,
        phone=None,
        wallet_address=None,
        total_contributions=0,
        is_active=True,
    ):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            profile_picture=profile_picture,
            bio=bio,
            phone=phone,
            wallet_address=wallet_address,
            total_contributions=total_contributions,
            is_active=is_active,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email,
        password,
        username,
        wallet_address="adminwalletaddress",
    ):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            username=username,
            wallet_address=wallet_address,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


def get_users_files_directory(instance, filename):
    if type(instance) is User:
        return f"users/{instance.username}/{filename}"


class LowerCaseCharField(models.CharField):
    def get_prep_value(self, value):
        return str(value).lower()


class User(AbstractBaseUser):
    username = models.CharField(max_length=20, unique=True, null=False, blank=False)
    email = LowerCaseCharField(max_length=254, unique=True, null=False, blank=False)
    password = models.CharField(max_length=254, null=False, blank=False)
    first_name = models.CharField(null=True, blank=True, max_length=50)
    last_name = models.CharField(null=True, blank=True, max_length=50)
    profile_picture = models.ImageField(
        blank=True,
        null=True,
        upload_to=get_users_files_directory,
    )
    bio = models.TextField(max_length=10000, null=True, blank=True, default="")
    phone = PhoneNumberField(null=True, blank=True)
    wallet_address = models.CharField(
        max_length=254, null=True, blank=True, default="None"
    )
    creation_datetime = models.DateTimeField(auto_now_add=True)
    total_contributions = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    password_reset_token = models.CharField(null=True, blank=True, max_length=254)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


def get_category_files_directory(instance, filename):
    return f"categories/{instance.name}/{filename}"


class Category(models.Model):
    name = models.CharField(max_length=254, null=False, blank=False, unique=True)
    image = models.ImageField(
        blank=False,
        null=False,
        default="help.jpg",
        upload_to=get_category_files_directory,
    )

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    name = models.CharField(max_length=254, null=False, blank=False, unique=True)
    category = models.ForeignKey(
        Category, null=False, blank=False, on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class Type(models.Model):
    name = models.CharField(max_length=245, null=False, blank=False, unique=True)

    def __str__(self):
        return self.name


class Country(models.Model):
    # All countries
    iso = models.CharField(max_length=2, null=True)
    name = models.CharField(max_length=254, null=True)
    nicename = models.CharField(max_length=254, null=True)
    iso3 = models.CharField(max_length=3, null=True)
    numcode = models.IntegerField(null=True)
    phonecode = models.IntegerField(null=True)

    def __str__(self):
        return self.name


class EligibleCountry(models.Model):
    # iso, name, nicename, iso3, numcode, phonecode
    # Countries which can crowdfund with us
    iso = models.CharField(max_length=2, null=True)
    name = models.CharField(max_length=254, null=True)
    nicename = models.CharField(max_length=254, null=True)
    iso3 = models.CharField(max_length=3, null=True)
    numcode = models.IntegerField(null=True)
    phonecode = models.IntegerField(null=True)

    def __str__(self):
        return self.name


def get_project_files_directory(instance, filename):
    if type(instance) is Project:
        return f"projects/{instance.id}/{instance.title}/{filename}"
    elif type(instance) is ProjectFile:
        return f"projects/{instance.owner.id}/{instance.owner.title}/{filename}"


class Project(models.Model):
    # Basics
    owner = models.ForeignKey(User, null=True, blank=False, on_delete=models.SET_NULL)
    title = models.CharField(max_length=254, null=True, blank=False, unique=True)
    head = models.TextField(max_length=280, null=True, blank=False)
    country = models.ForeignKey(
        EligibleCountry, null=True, blank=False, on_delete=models.SET_NULL
    )
    address = models.CharField(max_length=254, null=True, blank=False)
    thumbnail = models.ImageField(
        blank=False,
        null=True,
        default="help.jpg",
        upload_to=get_project_files_directory,
    )
    creation_datetime = models.DateTimeField(null=True, auto_now_add=True)
    launch_date = models.DateTimeField(null=True, default=None)
    deadline = models.DateTimeField(null=True, default=None)
    category = models.ForeignKey(
        Category, null=True, blank=False, on_delete=models.SET_NULL
    )
    subcategory = models.ForeignKey(
        Subcategory, blank=True, null=True, on_delete=models.SET_NULL
    )
    type = models.ForeignKey(Type, null=True, blank=False, on_delete=models.SET_NULL)
    # Funding
    fund_amount = models.FloatField(null=True, blank=False)
    # Story
    description = RichTextField(
        max_length=10000,
        null=True,
        blank=False,
        external_plugin_resources=[
            (
                "youtube",
                "https://rarefnd-bucket.s3.us-east-2.amazonaws.com/ckeditor/ckeditor/plugins/youtube/youtube/",
                "plugin.js",
            ),
            (
                "html5video",
                "https://rarefnd-bucket.s3.us-east-2.amazonaws.com/ckeditor/ckeditor/plugins/html5_video/html5video/",
                "plugin.js",
            ),
        ],
    )
    # Payment
    company_name = models.CharField(max_length=254, null=True, blank=False)
    company_nature_of_business = models.CharField(
        max_length=254, null=True, blank=False
    )
    company_address = models.CharField(max_length=254, null=True, blank=False)
    company_city = models.CharField(max_length=254, null=True, blank=False)
    company_zip_code = models.CharField(max_length=254, null=True, blank=False)
    company_country = models.ForeignKey(
        EligibleCountry,
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name="company_tax_country",
    )
    company_incorporation_date = models.DateTimeField(null=True, default=None)
    company_registration_number = models.CharField(
        max_length=254, null=True, blank=False
    )
    company_estimated_annual_turnover = models.CharField(
        max_length=254, null=True, blank=False
    )
    company_tax_country = models.ForeignKey(
        EligibleCountry,
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name="ubo_company_tax_country",
    )

    company_tax_identification_number = models.CharField(
        max_length=254, null=True, blank=False
    )
    # company_white_paper_url = models.CharField(max_length=1000, null=True, blank=True)
    # company_tokenomics_url = models.CharField(max_length=1000, null=True, blank=True)
    company_ubos = JSONField(null=True, default=dict, blank=True)
    wallet_address = models.CharField(max_length=254, null=True, blank=True)

    current_reward = models.FloatField(null=False, blank=False, default=0)
    raised_amount = models.FloatField(null=True, blank=True, default=0)
    rewarded_amount = models.FloatField(null=True, blank=True, default=0)
    staking_address = models.CharField(max_length=254, null=True, blank=True)
    staking_abi = models.TextField(max_length=10000, null=True, blank=True)
    approved = models.BooleanField(default=False)
    live = models.BooleanField(default=False)
    project_live_datetime = models.DateTimeField(null=True, default=None, blank=True)
    subscribed_users = models.ManyToManyField(
        User, related_name="Projects", default=None, blank=True
    )

    @property
    def number_of_subscribed_users(self):
        return self.subscribed_users.count()

    @property
    def owner_username(self):
        return self.owner.username

    @property
    def owner_profile_picture(self):
        return (
            self.owner.profile_picture.url
            if self.owner.profile_picture
            else "https://rarefnd-bucket.s3.us-east-2.amazonaws.com/users/avatar.jpg"
        )

    @property
    def number_of_donators(self):
        # return len(Contribution.objects.filter(project=self))
        return len(
            Contribution.objects.filter(project=self)
            .values("contributor_wallet_address")
            .distinct()
        )

    def __str__(self):
        return self.title


class ProjectFile(models.Model):
    owner = models.ForeignKey(
        Project, null=True, blank=False, on_delete=models.SET_NULL
    )
    file = models.FileField(
        validators=[
            FileExtensionValidator(
                allowed_extensions=["gif", "png", "jpg", "jpeg", "xlsx", "csv", "pdf"]
            )
        ],
        upload_to=get_project_files_directory,
    )

    def __str__(self):
        return f"{self.owner} | {self.file}"


def get_rare_fnd_data_files_directory(instance, filename):
    return f"RareFNDData/{filename}"


class RareFndData(models.Model):
    white_paper = models.FileField(
        upload_to=get_rare_fnd_data_files_directory,
    )


class Incentive(models.Model):
    title = models.CharField(max_length=50, null=False, blank=False)
    description = models.TextField(max_length=254, null=False, blank=False)
    included_incentives = JSONField(null=True, default=list)
    estimated_delivery = models.DateTimeField(null=False, blank=False)
    available_items = models.IntegerField(null=False, blank=False)
    price = models.FloatField(null=False, blank=False)
    reserved = models.IntegerField(blank=True, default=0)
    project = models.ForeignKey(
        Project, null=False, blank=False, on_delete=models.CASCADE
    )

    def __str__(self):
        return self.title


class Contribution(models.Model):
    contributor_wallet_address = models.CharField(max_length=254, null=True, blank=True)
    project = models.ForeignKey(
        Project, null=False, blank=False, on_delete=models.CASCADE
    )
    amount = models.FloatField(null=False, blank=False)
    contribution_datetime = models.DateTimeField(auto_now_add=True)
    hash = models.CharField(max_length=254, null=False, blank=False, unique=True)

    def __str__(self):
        return f"{self.project} {self.contributor_wallet_address}"


class PendingContribution(models.Model):
    hash = models.CharField(max_length=254, null=False, blank=False, unique=True)
    project = models.ForeignKey(
        Project, null=False, blank=False, on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.hash} {self.project}"


class Release(models.Model):
    title = models.CharField(max_length=254, null=False, blank=False)
    description = RichTextField(max_length=10000)
    project = models.ForeignKey(
        Project, null=False, blank=False, on_delete=models.CASCADE
    )
    release_datetime = models.DateTimeField(auto_now_add=True)
    release_amount = models.FloatField(null=False, blank=False)

    def __str__(self):
        return f"{self.title} {self.project}"


class TokenPrice(models.Model):
    price = models.FloatField(blank=False, null=False)
    price_datetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.price} {self.price_datetime}"


class MercuryoPendingStake(models.Model):
    wallet_address = models.CharField(
        max_length=254, null=True, blank=True, default="None"
    )
    smart_contract_address = models.CharField(
        max_length=254, null=True, blank=True, default="None"
    )
    usd_amount = models.FloatField(default=0)
    bnb_amount = models.FloatField(default=0)
    project_id = models.IntegerField(default=0)
    staking_transaction_hash = models.CharField(
        max_length=254, null=True, blank=True, default="None"
    )
    contribution_datetime = models.DateTimeField(
        auto_now_add=True, blank=False, null=False
    )

    def __str__(self):
        return f"{self.wallet_address} {self.smart_contract_address} {self.usd_amount} | {self.contribution_datetime}"
