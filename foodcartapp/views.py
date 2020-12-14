import json

from datetime import datetime
from typing import OrderedDict

from django.http import JsonResponse
from django.templatetags.static import static

from .models import Order, OrderProduct
from .models import Product
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse(
        [
            {
                "title": "Burger",
                "src": static("burger.jpg"),
                "text": "Tasty Burger at your door step",
            },
            {
                "title": "Spices",
                "src": static("food.jpg"),
                "text": "All Cuisines",
            },
            {
                "title": "New York",
                "src": static("tasty.jpg"),
                "text": "Food is incomplete without a tasty dessert",
            },
        ],
        safe=False,
        json_dumps_params={
            "ensure_ascii": False,
            "indent": 4,
        },
    )


def product_list_api(request):
    products = Product.objects.select_related("category").available()

    dumped_products = []
    for product in products:
        dumped_product = {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "special_status": product.special_status,
            "description": product.description,
            "category": {
                "id": product.category.id,
                "name": product.category.name,
            },
            "image": product.image.url,
            "restaurant": {
                "id": product.id,
                "name": product.name,
            },
        }
        dumped_products.append(dumped_product)
    return JsonResponse(
        dumped_products,
        safe=False,
        json_dumps_params={
            "ensure_ascii": False,
            "indent": 4,
        },
    )


@api_view(["GET", "POST"])
def register_order(request):
    try:
        if request.method == "GET":
            return Response()
        order_data = request.data
        if not check_valid(order_data):
            raise ValueError()
        order = Order.objects.create(
            address=order_data["address"],
            firstname=order_data["firstname"],
            lastname=order_data["lastname"],
            phonenumber=order_data["phonenumber"],
        )

        for i in order_data["products"]:
            ordered_product = OrderProduct.objects.create(
                product=Product.objects.get(id=int(i["product"])),
                quantity=int(i["quantity"]),
                order=order,
            )
            order.ordered_products.add(ordered_product)
        order.save()

        return Response({"id": 1, "message": "Created"})
    except ValueError:
        return Response(
            {
                "error": "cannot parse json order",
            }, 
            status=status.HTTP_406_NOT_ACCEPTABLE
        )

def check_valid(data):
    if len(data.keys()) != 5:
        return False
    if type(data["products"]) != list or not data["products"]:
        return False
    if any([x.isdigit() for x in data["firstname"]]):
        return False
    if any([x.isdigit() for x in data["lastname"]]):
        return False
    if len(data["phonenumber"]) < 4:
        return False
    if len(data["address"]) < 10:
        return False