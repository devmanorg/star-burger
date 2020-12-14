from django.urls import path, include

from .views import product_list_api, banners_list_api, register_order
from rest_framework import urls


app_name = "foodcartapp"

urlpatterns = [
    path("products/", product_list_api),
    path("banners/", banners_list_api),
    path("order/", register_order),
]
