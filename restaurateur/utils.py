import requests

from django.conf import settings

from geopy import distance
from requests.exceptions import RequestException

from locationapp.models import Location
from django.utils import timezone
from datetime import timedelta


def fetch_coordinates(address):
    try:
        location = Location.objects.get(location_address=address)
        if timezone.now().date() - location.created_at < timedelta(days=7):
            return location.longitude, location.latitude
    except Location.DoesNotExist:
        location = None

    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": settings.YANDEX_API_KEY,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")

    if location:
        location.longitude = lon
        location.latitude = lat
        location.created_at = timezone.now().date() 
        location.save()
    else:
        Location.objects.create(location_address=address, longitude=lon, latitude=lat)

    return lon, lat


def fetch_order_and_restaurant_coordinates(order_address, restaurant_address):
    order_coordinate = None
    restaurant_coordinates = []
    try:
        if order_address:
            order_coordinate = fetch_coordinates(order_address)
    except RequestException:
        order_coordinate = None

    for restaurant in restaurant_address:
        try:
            restaurant_coordinates.append(fetch_coordinates(restaurant.address))
        except RequestException:
            continue

    return order_coordinate, restaurant_coordinates


def get_distance(restaurants_cordinate, order_coordinate, order_possible_restaurants):
    if not order_coordinate:
        return []

    distances = []
    for coord in restaurants_cordinate:
        distances.append(distance.distance(tuple(reversed(order_coordinate)), tuple(reversed(coord))).km)

    restaurants_with_distance = list(zip(order_possible_restaurants, distances))
    restaurants_with_distance.sort(key=lambda x: x[1])
    return restaurants_with_distance