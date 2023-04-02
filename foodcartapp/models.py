from collections import defaultdict

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Sum
from phonenumber_field.modelfields import PhoneNumberField


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


class ProductOrder(models.Model):
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='orders',
    )
    order = models.ForeignKey(
        'Order',
        on_delete=models.CASCADE,
        related_name='products_ordered'
    )
    quantity = models.PositiveIntegerField('количество')
    product_price = models.DecimalField(
        'цена товара',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True,
    )

    def __str__(self):
        return f'{self.product}, {self.quantity}'


class OrderQuerySet(models.QuerySet):
    def with_totals(self):
        return self.annotate(total=Sum(F('products_ordered__product_price') * F('products_ordered__quantity')))


class Order(models.Model):

    class Status(models.IntegerChoices):
        NEW = 0, 'Не обработан'
        PREPARING = 1, 'Готовится'
        DELIVERING = 2, 'В пути'
        COMPLETE = 3, 'Доставлен'

    class PaymentMethod(models.TextChoices):
        CASH = 'CASH', 'Наличные'
        CARD = 'CARD', 'Карта'
        __empty__ = ''

    firstname = models.CharField(
        'имя',
        max_length=50,
    )
    lastname = models.CharField(
        'фамилия',
        max_length=50,
        db_index=True,
    )
    phonenumber = PhoneNumberField(
        'телефон',
        db_index=True,
    )
    address = models.CharField(
        'адрес',
        max_length=200,
    )
    products = models.ManyToManyField(
        'Product',
        verbose_name='товары',
        related_name='order',
        through='ProductOrder',
    )
    status = models.SmallIntegerField(
        'статус',
        choices=Status.choices,
        default=Status.NEW,
        db_index=True,
    )
    comment = models.TextField(
        'комментарий',
        blank=True,
    )
    created_at = models.DateTimeField(
        'время создания',
        auto_now_add=True,
        db_index=True,
    )
    called_at = models.DateTimeField(
        'время звонка',
        blank=True,
        null=True,
        db_index=True,
    )
    delivered_at = models.DateTimeField(
        'когда доставлен',
        blank=True,
        null=True,
        db_index=True,
    )
    payment_method = models.CharField(
        'способ оплаты',
        choices=PaymentMethod.choices,
        max_length=4,
        blank=True,
        null=True,
        db_index=True,
    )
    restaurant = models.ForeignKey(
        'Restaurant',
        verbose_name='ответственный ресторан',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='orders',
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'{self.id}: {self.firstname} {self.lastname[:1]}., {self.created_at:%d.%m.%y %H:%M:%S}'
