from django.db import models
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import F, Sum, Max



class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class TotalCost(models.QuerySet):
    def sum(self):
        return self.values('order_id').annotate(
            total=Sum(F('product__price')*F('quantity')),
            lastname=Max(F('order__lastname')),
            firstname=Max(F('order__firstname')),
            phonenumber=Max(F('order__phonenumber')),
            address=Max(F('order__address')),
            order=Max(F('order'))
        )


class Order(models.Model):
    address = models.CharField(
        'адрес',
        max_length=200,
        null=False,
    )
    firstname = models.CharField(
        'имя',
        max_length=50,
        null=False,
    )
    lastname = models.CharField(
        'фамилия',
        max_length=50,
        null=False,
        db_index=True,
    )
    phonenumber = PhoneNumberField()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

        def __str__(self):
            return self.name

class OrderLine(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='lines',
        verbose_name='номер заказа'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='lines',
        verbose_name='продукт'
    )
    quantity = models.PositiveSmallIntegerField(
        verbose_name='количество'
    )
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name='Цена',
        default=0,
        validators=[MinValueValidator(0)],
    )
    orders = TotalCost.as_manager()
    objects = models.Manager()

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

        def __str__(self):
            return self.name
