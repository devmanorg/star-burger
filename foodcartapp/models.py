from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import F, Sum


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
    def total(self, exclude_status='CT'):
        return self.exclude(status=exclude_status).annotate(
            total=Sum(F('lines__price')*F('lines__quantity')),
        )


class Order(models.Model):
    ORDER_STATUS_INT = [
        (1, 'Создан'),
        (2, 'Сборка'),
        (3, 'Доставка'),
        (4, 'Выполнен'),
    ]
    status_int = models.PositiveSmallIntegerField(
        verbose_name='Статус заказа',
        choices=ORDER_STATUS_INT,
        default=1,
        db_index=True,
    )
    cook_by = models.ForeignKey(
        Restaurant,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Исполнитель',
    )
    payment_type = models.CharField(
        max_length=4,
        choices=[
            ('CASH', 'наличные'),
            ('CARD', 'электронно'),
        ],
        default='CASH',
        verbose_name='способ оплаты',
        db_index=True,
    )
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
    phonenumber = PhoneNumberField(verbose_name='Телефон')
    comment = models.TextField(
        blank=True,
        max_length=200,
        verbose_name='комментарий'
    )
    created_at = models.DateTimeField(
        verbose_name='Создан',
        default=timezone.now,
        db_index=True
    )
    called_at = models.DateTimeField(
        verbose_name='Согласован',
        blank=True,
        null=True,
        db_index=True
    )
    delivered_at = models.DateTimeField(
        verbose_name='Доставлен',
        blank=True,
        null=True,
        db_index=True
    )

    price = TotalCost.as_manager()
    objects = models.Manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'Заказ №{self.id}'


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

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'
