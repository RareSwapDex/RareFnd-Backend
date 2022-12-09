"""RareFND URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include, re_path
from RareFndApp import views, tasks
from rest_framework import routers
from django.views.static import serve
from django.conf import settings
import threading
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from RareFndApp.serializers import MyTokenObtainPairView
from django_email_verification import urls as email_urls


t1 = threading.Thread(target=tasks.start_tasks)
t1.start()

router = routers.DefaultRouter()

# register the router
# router.register('project/',views.projects_list)
# router.register(r'category',views.CategorytView, 'category')

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/user/signup/", views.signup_user),
    path("api/user/profile_info/", views.get_profile_info),
    path("api/user/update/", views.update_user),
    path("api/incentives/<int:project_id>/", views.incentives),
    path("api/profile/<int:user_id>/", views.user_info),
    path("api/user/verify_email/", include(email_urls)),
    path("api/rarefnd/data/", views.get_rare_fnd_data),
    path("api/unique/<str:field_to_check>/<str:field_value>/", views.unique_record),
    path("api/project/category/<str:category_name>/", views.projects_from_category),
    path("api/project/add/", views.add_project),
    path("api/project/ckeditor/upload_image", views.upload_ckeditor_image),
    path(
        "api/project/checked_subscribed/<int:projectId>/",
        views.check_subscribed_to_project,
    ),
    path("api/project/subscribe/", views.subscribe_to_project),
    path(
        "api/category/<str:category_name>/subcategories/",
        views.subcategories_list_of_category,
    ),
    path("api/country/", views.countries_list),
    path("api/eligible_country/", views.eligible_countries_list),
    path("api/contribution/", views.contributions_list),
    path("api/pending_contribution/", views.pending_contributions_list),
    path("api/project/", views.projects_list),
    path("api/category/", views.categories_list),
    path("api/price/", views.token_price),
    path("api/project/<int:id>/", views.projects_details_by_id),
    path("api/projects/<str:title>/", views.projects_details_by_title),
    path("api/project/title/", views.projects_details_by_title),
    path("", include("RareFndApp.urls")),
    path("tinymce/", include("tinymce.urls")),
    re_path(
        r"^files/(?P<path>.*)$",
        serve,
        {
            "document_root": settings.MEDIA_ROOT,
        },
    ),
    path("api/auth/token/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path(
        "api/venly/create_wallet/<str:email>/<int:usd_amount>/<str:smart_contract_address>/<int:project_id>",
        views.venly_create_wallet,
    ),
    path("api/mercuryo/payment_callback/", views.mercuryo_callback_wallet_received_bnb),
    # kk
    path("api/auth/venly_auth/", views.get_venly_auth),
    path("api/venly_execute_swap/", views.venly_execute_swap),
]
