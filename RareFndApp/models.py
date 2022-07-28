from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class User(models.Model):
    username = models.CharField(max_length=20, unique=True, null=False, blank=False)
    password = models.CharField(max_length=254, null=False, blank=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    phone = PhoneNumberField()
    creation_datetime = models.DateTimeField(auto_now_add=True)
    total_contributions = models.IntegerField(default=0)
    

class Category(models.Model):
    name = models.CharField(max_length=254, null=False, blank=False, unique=True)


class Subcategory(models.Model):
    name = models.CharField(max_length=254, null=False, blank=False, unique=True)
    category = models.ForeignKey(Category, null=False, blank=False, on_delete=models.CASCADE)


class Type(models.Model):
    name = models.CharField(max_length=245, null=False, blank=False, unique=True)


class Country(models.Model):
    name = models.CharField(max_length=254, null=False, blank=False, unique=True)
    phone_code = models.CharField(max_length=16, null=False, blank=False, unique=True)


class Project(models.Model):
    owner = models.ForeignKey(User, null=True, blank=False, on_delete=models.SET_NULL)
    name = models.CharField(max_length=254, null=False, blank=False)
    description = models.CharField(max_length=10000, null=False, blank=False)
    type = models.ForeignKey(Type, null=True, blank=False, on_delete=models.SET_NULL)
    category = models.ForeignKey(Category, null=True, blank=False, on_delete=models.SET_NULL)
    subcategory = models.ForeignKey(Subcategory, null=True, on_delete=models.SET_NULL)
    country = models.ForeignKey(Country, null=True, blank=False, on_delete=models.SET_NULL)
    address = models.CharField(max_length=254, null=False, blank=False)
    creation_datetime = models.DateTimeField(auto_now_add=True)
    fund_amount = models.PositiveBigIntegerField(null=False, blank=False)
    wallet_address = models.CharField(max_length=254, null=False, blank=False)
    deadline = models.DateTimeField()


class LegalPaper(models.Model):
    name = models.CharField(max_length=254, null=False, blank=False)
    location = models.CharField(max_length=10000, null=False, blank=False)
    project = models.ForeignKey(Project, null=False, blank=False, on_delete=models.CASCADE)


class Contribution(models.Model):
    contributor = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, null=False, blank=False, on_delete=models.CASCADE)
    amount = models.PositiveBigIntegerField(null=False, blank=False)
    contribution_datetime = models.DateTimeField(auto_now_add=True)


class Release(models.Model):
    title = models.CharField(max_length=254, null=False, blank=False)
    description = models.CharField(max_length=10000)
    project = models.ForeignKey(Project, null=False, blank=False, on_delete=models.CASCADE)
    release_datetime = models.DateTimeField(auto_now_add=True)
    release_amount = models.PositiveBigIntegerField(null=False, blank=False)
