from django.contrib import admin
from .models import GeoCache

@admin.register(GeoCache)
class GeoCacheAdmin(admin.ModelAdmin):
    model = GeoCache


