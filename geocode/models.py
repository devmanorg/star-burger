from django.db import models
from django.utils import timezone
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


def get_geo(venues):
    restaurant_geo = GeoCache.objects.filter(
        address__in=venues.values('address')
    )
    restaurant_addresses = []
    for restaurant in restaurant_geo:
        restaurant_addresses.append(restaurant.address)
    print(restaurant_addresses)
    for venue in venues:
        if venue.address in restaurant_addresses:
            print(venue.id)
