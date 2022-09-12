from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from ckeditor.fields import RichTextField
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.core.validators import FileExtensionValidator


class UserManager(BaseUserManager):
    def create_user(
        self,
        email,
        username,
        password,
        first_name=None,
        last_name=None,
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


class User(AbstractBaseUser):
    username = models.CharField(max_length=20, unique=True, null=False, blank=False)
    email = models.EmailField(max_length=254, unique=True, null=False, blank=False)
    password = models.CharField(max_length=254, null=False, blank=False)
    first_name = models.CharField(null=True, blank=True, max_length=50)
    last_name = models.CharField(null=True, blank=True, max_length=50)
    phone = PhoneNumberField(null=True, blank=True)
    wallet_address = models.CharField(max_length=254, null=False, blank=False)
    creation_datetime = models.DateTimeField(auto_now_add=True)
    total_contributions = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
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
    name = models.CharField(max_length=254, null=False, blank=False, unique=True)
    phone_code = models.CharField(max_length=16, null=False, blank=False, unique=True)

    def __str__(self):
        return self.name


def get_project_files_directory(instance, filename):
    return f"projects/{instance.title}/{filename}"


class Project(models.Model):
    owner = models.ForeignKey(User, null=True, blank=False, on_delete=models.SET_NULL)
    title = models.CharField(max_length=254, null=False, blank=False)
    head = models.TextField(max_length=280, null=False, blank=False)
    description = RichTextField(max_length=10000, null=False, blank=False)
    thumbnail = models.ImageField(
        blank=False,
        null=False,
        default="help.jpg",
        upload_to=get_project_files_directory,
    )
    files = models.FileField(
        # validators=[FileExtensionValidator(allowed_extensions=["jpeg", "png", "jpg"])]
        upload_to=get_project_files_directory,
    )
    type = models.ForeignKey(Type, null=True, blank=False, on_delete=models.SET_NULL)
    category = models.ForeignKey(
        Category, null=True, blank=False, on_delete=models.SET_NULL
    )
    subcategory = models.ForeignKey(Subcategory, null=True, on_delete=models.SET_NULL)
    country = models.ForeignKey(
        Country, null=True, blank=False, on_delete=models.SET_NULL
    )
    address = models.CharField(max_length=254, null=False, blank=False)
    creation_datetime = models.DateTimeField(auto_now_add=True)
    fund_amount = models.FloatField(null=False, blank=False)
    raised_amount = models.FloatField(null=False, blank=False, default=0)
    rewarded_amount = models.FloatField(null=False, blank=False, default=0)
    staking_address = models.CharField(max_length=254, null=False, blank=False)
    staking_abi = models.TextField(max_length=10000, null=False, blank=False)
    deadline = models.DateTimeField()
    aproved = models.BooleanField(default=False)
    live = models.BooleanField(default=False)
    project_live_datetime = models.DateTimeField(null=True, default=None, blank=True)

    def __str__(self):
        return self.title


def get_rare_fnd_data_files_directory(instance, filename):
    return f"RareFNDData/{filename}"


class RareFndData(models.Model):
    white_paper = models.FileField(
        upload_to=get_rare_fnd_data_files_directory,
    )


class Incentive(models.Model):
    title = models.CharField(max_length=50, null=False, blank=False)
    description = models.TextField(max_length=254, null=False, blank=False)
    included_incentives = models.CharField(max_length=1000, null=True, blank=True)
    estimated_delivery = models.DateField(null=False, blank=False)
    available_items = models.IntegerField(null=False, blank=False)
    price = models.FloatField(null=False, blank=False)
    reserved = models.IntegerField(blank=True)
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
