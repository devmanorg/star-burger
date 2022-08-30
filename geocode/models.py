from django.db import models
from django.utils import timezone
from django.conf import settings

import requests
import datetime

from django.db.models.signals import post_save
from django.dispatch import receiver

from foodcartapp.models import Restaurant


class GeoCache(models.Model):
    address = models.CharField(
        'адрес',
        max_length=100,
        unique=True,
    )
    lat = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        null=True,
        verbose_name='широта'
    )
    lon = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        null=True,
        verbose_name='долгота'
    )
    timestamp = models.DateField(
        verbose_name='обновлено',
        default=timezone.now,
    )

    class Meta:
        verbose_name = 'Геопозиция'
        verbose_name_plural = 'Геопозиции'

    def __str__(self):
        return self.address


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
