import requests
import datetime

from .models import GeoCache
from django.conf import settings
from django.utils import timezone


def create_or_update_coordinates(address, apikey=settings.API_YANDEX_TOKEN):
    geo_point = GeoCache.objects.filter(address=address).first()
    if geo_point:
        if geo_point.timestamp - timezone.now().date() < \
                datetime.timedelta(days=7):
            return geo_point.lat, geo_point.lon
    base_url = "https://geocode-maps.yandex.ru/1.x"
    try:
        response = requests.get(base_url, params={
            "geocode": address,
            "apikey": apikey,
            "format": "json",
        })
        response.raise_for_status()
    except Exception as _:
        return None

    found_places = response. \
        json()['response']['GeoObjectCollection']['featureMember']
    if not found_places:
        try:
            GeoCache.objects.create(address=address)
        except Exception as _:
            pass
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    try:
        GeoCache.objects.create(
            address=address,
            lat=lat,
            lon=lon,
        )
    except Exception as _:
        pass
    return lat, lon
