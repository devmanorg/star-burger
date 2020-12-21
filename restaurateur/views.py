import urllib

import requests
from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from django.core.cache import cache
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from geopy import distance
from foodcartapp.models import Product, Restaurant, Order, RestaurantMenuItem


class Login(forms.Form):
    username = forms.CharField(
        label="Логин",
        max_length=75,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Укажите имя пользователя",
            },
        ),
    )
    password = forms.CharField(
        label="Пароль",
        max_length=75,
        required=True,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Введите пароль"},
        ),
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={"form": form})

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(
            request,
            "login.html",
            context={
                "form": form,
                "ivalid": True,
            },
        )


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy("restaurateur:login")


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url="restaurateur:login")
def view_products(request):
    restaurants = list(Restaurant.objects.order_by("name"))
    products = list(Product.objects.prefetch_related("menu_items"))

    default_availability = {restaurant.id: False for restaurant in restaurants}
    products_with_restaurants = []
    for product in products:

        availability = {
            **default_availability,
            **{
                item.restaurant_id: item.availability
                for item in product.menu_items.all()
            },
        }
        orderer_availability = [
            availability[restaurant.id] for restaurant in restaurants
        ]

        products_with_restaurants.append((product, orderer_availability))

    return render(
        request,
        template_name="products_list.html",
        context={
            "products_with_restaurants": products_with_restaurants,
            "restaurants": restaurants,
        },
    )


@user_passes_test(is_manager, login_url="restaurateur:login")
def view_restaurants(request):
    return render(
        request,
        template_name="restaurants_list.html",
        context={
            "restaurants": Restaurant.objects.all(),
        },
    )


@user_passes_test(is_manager, login_url="restaurateur:login")
def view_orders(request):
    orders = Order.objects.all()
    orders_list = [serialize_order(order) for order in orders]
    return render(
        request,
        template_name="order_items.html",
        context={"orders": orders_list},
    )


def get_coords(address):
    payload = {"q": address, "polygon_geojson": 1, "format": "jsonv2"}
    url = "https://nominatim.geocoding.ai/search.php"
    try:
        adr_key = urllib.parse.quote(address.strip().lower())
        if cache.get(adr_key):
            return cache.get(adr_key)
        res = requests.get(url, params=payload)
        if res.ok:
            json_data = res.json()
            lat, lon = float(json_data[0]["lat"]), float(json_data[0]["lon"])
            cache.set(adr_key, [lat, lon], 3600)
            return lat, lon
    except Exception:
        return None


def get_distance(coord1, coord2):
    try:
        return distance.distance(coord1, coord2).km
    except Exception:
        return None


def serialize_order(order):
    order_coords = get_coords(order.address)
    prods = [x.product for x in order.ordered_products.all()]
    items_lists = [RestaurantMenuItem.objects.filter(product=x) for x in prods]
    rest_lists = []

    for item_list in items_lists:
        rest_list = []
        for x in item_list:
            coords = get_coords(x.restaurant.address)
            dist = get_distance(order_coords, coords)
            rest_list.append(
                {"name": x.restaurant.name, "distance": round(dist, 2)},
            )
        rest_lists.append(rest_list)

    print(rest_lists)
    return {
        "id": order.id,
        "client": f"{order.firstname} {order.lastname}",
        "price": order.get_price(),
        "phonenumber": order.phonenumber.as_international,
        "address": order.address,
        "status": order.get_status_display(),
        "comment": order.comment,
        "payment": order.get_payment_display(),
        "available_in": rest_lists,
    }
