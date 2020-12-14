import json

from datetime import datetime
from typing import OrderedDict

from django.http import JsonResponse
from django.templatetags.static import static

from .models import Order, OrderProduct
from .models import Product
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import (
    ValidationError,
    Serializer,
    CharField,
    ListField,
    IntegerField
)
from rest_framework import status

class ProductSerailizer(Serializer):
    product=IntegerField()
    quantity=IntegerField()

class OrderSerializer(Serializer):
    products = ListField(child=ProductSerailizer())
    firstname = CharField()
    lastname = CharField()
    phonenumber = CharField()
    address = CharField()

    def validate_products(self, value):
        if not value:
            raise ValidationError("Bad product list")
        return value

    def validate_firstname(self, value):
        if any([letter.isdigit() for letter in value]) or len(value) < 3:
            raise ValidationError("Wrong firstname")
        return value

    def validate_lastname(self, value):
        if any([letter.isdigit() for letter in value]) or len(value) < 3:
            raise ValidationError("Wrong lastname")
        return value

    def validate_phonenumber(self, value):
        valid_chars = "0123456789-+()"
        if len(value) < 4 or any(
            [char for char in value if char not in valid_chars]
        ):
            raise ValidationError("Wrong phonenumber")
        return value

    def validate_address(self, value):
        if len(value) < 5:
            raise ValidationError("Wrong value")
        return value


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
        serializer = OrderSerializer(data=order_data)
        serializer.is_valid(raise_exception=True)

        order = Order.objects.create(
            address=serializer.validated_data["address"],
            firstname=serializer.validated_data["firstname"],
            lastname=serializer.validated_data["lastname"],
            phonenumber=serializer.validated_data["phonenumber"],
        )

        for product_info in serializer.validated_data["products"]:
            ordered_product = OrderProduct.objects.create(
                product=Product.objects.get(id=int(product_info["product"])),
                quantity=int(product_info["quantity"]),
                order=order,
            )
            order.ordered_products.add(ordered_product)
        order.save()

        return Response(
            {"id": order.id, "message": "Created"},
            status=status.HTTP_201_CREATED,
        )
    except ValueError as e:
        return Response(
            {
                "error": "cannot parse json order",
            },
            status=status.HTTP_406_NOT_ACCEPTABLE,
        )
