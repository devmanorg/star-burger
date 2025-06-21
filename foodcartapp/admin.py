from django.contrib import admin
from django.shortcuts import reverse
from django.templatetags.static import static
from django.utils.html import format_html
from django.conf import settings
from django.utils.http import url_has_allowed_host_and_scheme
from django.http import HttpResponseRedirect

from .models import (
    Product,
    ProductCategory,
    Restaurant,
    RestaurantMenuItem,
    Order,
    OrderItem
)


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'address',
        'contact_phone',
    ]
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        RestaurantMenuItemInline
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'name',
        'category',
        'price',
    ]
    list_display_links = [
        'name',
    ]
    list_filter = [
        'category',
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly, so search will be buggy.
        # Migration to PostgreSQL is necessary
        'name',
        'category__name',
    ]

    inlines = [
        RestaurantMenuItemInline
    ]
    fieldsets = (
        ('Общее', {
            'fields': [
                'name',
                'category',
                'image',
                'get_image_preview',
                'price',
            ]
        }),
        ('Подробно', {
            'fields': [
                'special_status',
                'description',
            ],
            'classes': [
                'wide'
            ],
        }),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    class Media:
        css = {
            "all": (
                static("admin/foodcartapp.css")
            )
        }

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'
        return format_html('<img src="{url}" style="max-height: 200px;"/>', url=obj.image.url)
    get_image_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return 'нет картинки'
        edit_url = reverse('admin:foodcartapp_product_change', args=(obj.id,))
        return format_html('<a href="{edit_url}"><img src="{src}" style="max-height: 50px;"/></a>', edit_url=edit_url, src=obj.image.url)
    get_image_list_preview.short_description = 'превью'


@admin.register(ProductCategory)
class ProductAdmin(admin.ModelAdmin):
    pass


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'get_order_number',
        'firstname',
        'lastname',
        'address',
    )
    fields = (
        'status',
        'payment',
        'firstname',
        'lastname',
        'address',
        'phonenumber',
        'comment',
        'created_at',
        'called_at',
        'delivered_at',
        'restaurant_prepare'
    )
    inlines = [OrderItemInline]

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for instance in instances:
            if not instance.price_at_order:
                instance.price_at_order = instance.product.price*instance.quantity
            instance.save()

        formset.save_m2m()

    def response_change(self, request, obj):
        next_url = request.GET.get('next')
        if next_url and url_has_allowed_host_and_scheme(next_url, settings.ALLOWED_HOSTS):
            return HttpResponseRedirect(next_url)
        return super().response_change(request, obj)

    def get_order_number(self, obj):
        return f'Заказ - {obj.id}'
    get_order_number.short_description = 'Заказ'