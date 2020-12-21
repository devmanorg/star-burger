from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField("название", max_length=50)
    address = models.CharField("адрес", max_length=100, blank=True)
    contact_phone = models.CharField(
        "контактный телефон",
        max_length=50,
        blank=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "ресторан"
        verbose_name_plural = "рестораны"


class ProductQuerySet(models.QuerySet):
    def available(self):
        return self.distinct().filter(menu_items__availability=True)


class ProductCategory(models.Model):
    name = models.CharField("название", max_length=50)

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "категории"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField("название", max_length=50)
    category = models.ForeignKey(
        ProductCategory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="категория",
        related_name="products",
    )
    price = models.DecimalField("цена", max_digits=8, decimal_places=2)
    image = models.ImageField("картинка")
    special_status = models.BooleanField(
        "спец.предложение",
        default=False,
        db_index=True,
    )
    description = models.TextField("описание", max_length=200, blank=True)

    objects = ProductQuerySet.as_manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "товар"
        verbose_name_plural = "товары"


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="menu_items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="menu_items",
    )
    availability = models.BooleanField(
        "в продаже",
        default=True,
        db_index=True,
    )

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"

    class Meta:
        verbose_name = "пункт меню ресторана"
        verbose_name_plural = "пункты меню ресторана"
        unique_together = [["restaurant", "product"]]


class OrderProduct(models.Model):
    product = models.ForeignKey(
        "Product",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    quantity = models.IntegerField()
    order = models.ForeignKey(
        "Order",
        on_delete=models.CASCADE,
        related_name="products",
    )
    price = models.IntegerField(default=0)

    def __str__(self):
        return f"Заказ №{self.order.id}; {self.product.name}; В количестве {self.quantity}"

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"


class Order(models.Model):
    STATUS_CHOICES = (("Handled", "Обработано"), ("Unhandled", "Необработано"))
    PAYMENT_CHOICES = (("CASH", "Наличными"), ("CARD", "Электронно"))
    ordered_products = models.ManyToManyField(
        "OrderProduct",
        related_name="source",
    )
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    phonenumber = PhoneNumberField(region="RU")
    address = models.CharField(max_length=255)
    status = models.CharField(
        choices=STATUS_CHOICES,
        default="Unhandled",
        max_length=125,
    )
    comment = models.TextField(default="", blank=True)
    registered_at = models.DateTimeField(default=timezone.now)
    called_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    payment = models.CharField(
        choices=PAYMENT_CHOICES,
        default="CARD",
        max_length=125,
    )

    def __str__(self):
        return f"{self.firstname} {self.lastname} -> {self.address}"

    def get_price(self):
        return self.ordered_products.aggregate(models.Sum("price"))[
            "price__sum"
        ]

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
