from copy import copy

from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from geopy import distance

from foodcartapp.models import Product, Restaurant, Order, ProductOrder, RestaurantMenuItem
from places.models import Location


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
    active_orders = Order.objects.active().with_totals()
    active_product_orders = ProductOrder.objects.in_orders(active_orders)
    ordered_products = set(product_order.product for product_order in active_product_orders)
    ordered_menu_items = RestaurantMenuItem.objects.include_products(ordered_products)

    addresses = [order.address for order in active_orders] + [pr.restaurant.address for pr in ordered_menu_items]
    locations = Location.objects.filter(address__in=addresses)
    locations_by_address = {address: None for address in addresses}
    for location in locations:
        locations_by_address[location.address] = location

    for pr in ordered_menu_items:
        pr.restaurant.location = locations_by_address.get(pr.restaurant.address)

    for order in active_orders:
        order.location = locations_by_address.get(order.address)
        required_product_ids = [op.product.id for op in active_product_orders if op.order == order]
        order.available_restaurants = {
            copy(pr.restaurant) for pr in ordered_menu_items if pr.product.id in required_product_ids
        }
        for restaurant in order.available_restaurants:
            try:
                restaurant.distance = distance.distance(
                    (order.location.latitude, order.location.longitude),
                    (restaurant.location.latitude, restaurant.location.longitude),
                ).km
            except AttributeError:
                restaurant.distance = None
        order.available_restaurants = sorted(
            order.available_restaurants,
            key=lambda rest: rest.distance or 0,
        )

    return render(request, template_name='order_items.html', context={
        'orders': active_orders,
    })
