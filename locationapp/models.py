from django.db import models


class Location(models.Model):
    location_address = models.CharField(
        verbose_name='Адрес',
        max_length=100,
        unique=True,
    )
    longitude = models.DecimalField(
        verbose_name='Долгота',
        max_digits=9,
        decimal_places=6
    )
    latitude = models.DecimalField(
        verbose_name='Широта',
        max_digits=9,
        decimal_places=6
    )
    created_at = models.DateField(
        verbose_name="Дата запроса",
        auto_now=True
    )

    def __str__(self):
        return self.location_address