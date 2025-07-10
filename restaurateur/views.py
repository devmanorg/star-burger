from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.db.models import F, Sum

from locationapp.models import Location
from foodcartapp.models import Product, Restaurant, Order
from restaurateur.utils import fetch_order_and_restaurant_coordinates, get_distance


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    order_items = (
        Order.objects
        .select_related('restaurant_prepare')
        .prefetch_related('items__product')
        .annotate(price=Sum(F('items__quantity') * F('items__product__price')))
        .filter(status__in=['pending', 'in_progress', 'delivery'])
    )
    restaurants = Restaurant.objects.prefetch_related('menu_items__product')
    restaurant_products = {
        restaurant.id: set(menu_item.product for menu_item in restaurant.menu_items.all())
        for restaurant in restaurants
    }
    order_addresses = set(order.address for order in order_items)
    restaurant_addresses = set(restaurant.address for restaurant in restaurants)
    all_addresses = order_addresses.union(restaurant_addresses)
    locations = {loc.location_address: loc for loc in Location.objects.filter(location_address__in=all_addresses)}

    for order in order_items:
        products_in_order = set(item.product for item in order.items.all())
        possible_restaurants = [
            restaurant for restaurant in restaurants
            if products_in_order <= restaurant_products[restaurant.id]
        ]

        order_coordinate = (
            (locations.get(order.address).longitude,
             locations.get(order.address).latitude)
            if locations.get(order.address) else None
        )

        restaurants_cordinate = [
            (locations.get(restaurant.address).longitude,
             locations.get(restaurant.address).latitude
             ) for restaurant in possible_restaurants
        ]
        if order_coordinate and restaurants_cordinate:
            order.restaurants_with_distance = (
                get_distance(
                    restaurants_cordinate,
                    order_coordinate,
                    possible_restaurants)
            )
        else:
            order.coordinate, restaurant_coordinates = (
                fetch_order_and_restaurant_coordinates(
                    order_coordinate,
                    possible_restaurants)
            )
            order.restaurants_with_distance = (
                get_distance(
                    restaurant_coordinates,
                    order_coordinate,
                    possible_restaurants)
            )
        order.coord_error = order_coordinate is None

    return render(
        request,
        template_name='order_items.html',
        context={"order_items": order_items}
    )

