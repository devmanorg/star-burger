import requests

from django.conf import settings

from geopy import distance
from requests.exceptions import RequestException


def fetch_coordinates(address):
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
    return lon, lat


def fetch_order_and_restaurant_coordinates(order_address, restaurant_address):
    order_coordinate = None
    restaurant_coordinates = []
    try:
        if order_address:
            order_coordinate = tuple(reversed(fetch_coordinates(order_address)))
        for restaurant in restaurant_address:
            restaurant_coordinates.append(tuple(reversed(fetch_coordinates(restaurant.address))))
    except RequestException as req_err:
        print(f"Произошла ошибка при запросе: {req_err}")

    return order_coordinate, restaurant_coordinates


def get_distance(restaurant_coordinates, order_coordinate, order_possible_restaurants):
    distances = []
    for coord in restaurant_coordinates:
        distances.append(distance.distance(order_coordinate, coord).km)

    restaurants_with_distance = list(zip(order_possible_restaurants, distances))
    restaurants_with_distance.sort(key=lambda x: x[1])
    return restaurants_with_distance