import geopy.exc
from django.conf import settings
from django.db import models
from geopy import geocoders


class Location(models.Model):
    address = models.CharField(
        'адрес',
        max_length=200,
        unique=True,
    )
    latitude = models.FloatField(
        'широта',
        blank=True,
        null=True,
    )
    longitude = models.FloatField(
        'долгота',
        blank=True,
        null=True,
    )
    updated_at = models.DateTimeField(
        'обновлено',
        auto_now=True,
    )

    def __str__(self):
        return self.address

    @classmethod
    def update_by_address(cls, address):
        try:
            geocoder = geocoders.Yandex(api_key=settings.YANDEX_GEO_KEY)
            geo = geocoder.geocode(address)
            cls.objects.update_or_create(
                address=address,
                defaults={
                    'latitude': geo.latitude,
                    'longitude': geo.longitude,
                },
            )
        except (geopy.exc.GeocoderServiceError, AttributeError):
            cls.objects.get_or_create(
                address=address,
                defaults={
                    'latitude': None,
                    'longitude': None,
                },
            )
