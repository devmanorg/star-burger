import requests
import datetime

from .models import GeoCache
from foodcartapp.models import Restaurant, Order
from django.conf import settings
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


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


@receiver(post_save, sender=Restaurant)
def _(sender, instance, **kwargs):
    create_or_update_coordinates(instance.address)


@receiver(post_save, sender=Order)
def _(sender, instance, **kwargs):
    create_or_update_coordinates(instance.address)
