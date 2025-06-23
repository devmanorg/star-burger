from django.db import models
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
    MaxLengthValidator,
    MinLengthValidator
)
from django.utils.timezone import now

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


class Order(models.Model):
    ORDER_STATUS = (
        ('pending', 'Необработанный'),
        ('in_progress', 'В работе'),
        ('delivery', 'Доставка'),
        ('completed', 'Выполнен'),
        ('canceled', 'Отменен'),
    )
    PAYMENT_TYPE = (
        ('cash', 'Наличностью'),
        ('e_pay', 'Электронно'),
    )
    status = models.CharField(
        verbose_name='Статус заказа', 
        max_length=20, 
        choices=ORDER_STATUS, 
        default='pending'
    )
    firstname = models.CharField(
        verbose_name='Имя', 
        max_length=15, 
        validators=[MinLengthValidator(2), MaxLengthValidator(15)],
    )
    lastname = models.CharField(
        verbose_name='Фамилия', 
        max_length=15, 
        validators=[MinLengthValidator(3), MaxLengthValidator(15)],
    )
    phonenumber = PhoneNumberField(
        verbose_name='Телефон', 
        region='RU',
    )
    address = models.CharField(
        verbose_name='Адрес доставки', 
        max_length=45, 
        validators=[MinLengthValidator(4), MaxLengthValidator(45)],
    )
    comment = models.TextField(
        verbose_name='Комментарий', 
        max_length=100,
        blank=True,
    )
    created_at = models.DateTimeField(
        verbose_name="Создание заказа",
        default=now,
        blank=True,
        null=True,
    )
    called_at = models.DateTimeField(
        verbose_name="Время звонка",
        blank=True, 
        null=True
    )
    delivered_at = models.DateTimeField(
        verbose_name="Время доставки",
        blank=True,
        null=True
    )
    payment = models.CharField(
        verbose_name='Тип оплаты',
        max_length=20,
        choices=PAYMENT_TYPE,
        default='cash'
    )
    restaurant_prepare = models.ForeignKey(
        Restaurant,
        verbose_name='Ресторан готовит',
        related_name='cooking',
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f"{self.firstname} {self.lastname}, {self.address}"


class OrderItem(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_items',
        verbose_name='Товар',
    )
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='items', 
        verbose_name='заказ', 
    )
    quantity = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1), MaxValueValidator(99)]
    )
    price_at_order = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Цена",
    )

    class Meta:
        verbose_name = 'элемент заказа'
        verbose_name_plural = 'элементы заказа'

    def __str__(self):
        return f"{self.product.name} {self.order.firstname} {self.order.lastname} "
    
