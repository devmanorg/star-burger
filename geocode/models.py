from django.db import models
from django.utils import timezone


class GeoCache(models.Model):
    address = models.CharField(
        'адрес',
        max_length=100,
        unique=True,
    )
    lat = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        verbose_name='широта'
    )
    lon = models.DecimalField(
        max_digits=10,
        decimal_places=8,
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
