from pyexpat import model
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from ckeditor.fields import RichTextField
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    username = models.CharField(max_length=20, unique=True, null=False, blank=False)
    email = models.EmailField(max_length=254, unique=True, null=False, blank=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    password = models.CharField(max_length=254, null=False, blank=False)
    first_name = models.CharField(null=True, blank=True, max_length=50)
    last_name = models.CharField(null=True, blank=True, max_length=50)
    phone = PhoneNumberField(null=True, blank=True)
    wallet_address = models.CharField(max_length=254, null=False, blank=False)
    creation_datetime = models.DateTimeField(auto_now_add=True)
    total_contributions = models.IntegerField(default=0)
    is_active = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        user = super(User, self)
        user.set_password(self.password)
        user.save(*args, **kwargs)
        return user
    

def get_category_files_directory(instance, filename):
    return f"projects/{instance.name}/{filename}"

class Category(models.Model):
    name = models.CharField(max_length=254, null=False, blank=False, unique=True)
    image = models.ImageField(blank=False, null=False, default="help.jpg", upload_to=get_category_files_directory)
    
    def __str__(self):
        return self.name


class Subcategory(models.Model):
    name = models.CharField(max_length=254, null=False, blank=False, unique=True)
    category = models.ForeignKey(Category, null=False, blank=False, on_delete=models.CASCADE)
    
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
    thumbnail = models.ImageField(blank=False, null=False, default="help.jpg", upload_to=get_project_files_directory)
    files = models.FileField(blank=False, null=False, default="help.jpg", upload_to=get_project_files_directory)
    type = models.ForeignKey(Type, null=True, blank=False, on_delete=models.SET_NULL)
    category = models.ForeignKey(Category, null=True, blank=False, on_delete=models.SET_NULL)
    subcategory = models.ForeignKey(Subcategory, null=True, on_delete=models.SET_NULL)
    country = models.ForeignKey(Country, null=True, blank=False, on_delete=models.SET_NULL)
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

class Contribution(models.Model):
    contributor_wallet_address = models.CharField(max_length=254, null=True, blank=True)
    project = models.ForeignKey(Project, null=False, blank=False, on_delete=models.CASCADE)
    amount = models.FloatField(null=False, blank=False)
    contribution_datetime = models.DateTimeField(auto_now_add=True)
    hash = models.CharField(max_length=254, null=False, blank=False, unique=True)
    
    def __str__(self):
        return f'{self.project} {self.contributor_wallet_address}'

class PendingContribution(models.Model):
    hash = models.CharField(max_length=254, null=False, blank=False, unique=True)
    project = models.ForeignKey(Project, null=False, blank=False, on_delete=models.CASCADE)
    
    def __str__(self):
        return f'{self.hash} {self.project}'


class Release(models.Model):
    title = models.CharField(max_length=254, null=False, blank=False)
    description = RichTextField(max_length=10000)
    project = models.ForeignKey(Project, null=False, blank=False, on_delete=models.CASCADE)
    release_datetime = models.DateTimeField(auto_now_add=True)
    release_amount = models.FloatField(null=False, blank=False)
    
    def __str__(self):
        return f'{self.title} {self.project}'


class TokenPrice(models.Model):
    price = models.FloatField(blank=False, null=False)
    price_datetime = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.price} {self.price_datetime}'
