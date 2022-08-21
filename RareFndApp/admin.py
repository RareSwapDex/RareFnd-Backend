from django.contrib import admin
from RareFndApp.models import User, Category, Subcategory, Project, Type, Country, Contribution, Release, PendingContribution, TokenPrice, Incentive

# Register your models here.
admin.site.register(User)
admin.site.register(Project)
admin.site.register(Release)
admin.site.register(Contribution)
admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Type)
admin.site.register(Country)
admin.site.register(PendingContribution)
admin.site.register(TokenPrice)
admin.site.register(Incentive)
