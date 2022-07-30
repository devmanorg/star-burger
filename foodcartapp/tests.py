from django.test import TestCase
from foodcartapp.models import Restaurant, ProductCategory, Product, RestaurantMenuItem


class RestaurantModelTestcase(TestCase):
    @classmethod
    def setUpTestData(cls):
        Restaurant.objects.create(
            name="Random restaurant",
            address="Some address",
            contact_phone="+79991234567",
        )

    def test_string_method(self):
        restaurant = Restaurant.objects.get(pk=1)
        self.assertEqual(str(restaurant), restaurant.name)


class ProductCategoryModelTestcase(TestCase):
    @classmethod
    def setUpTestData(cls):
        ProductCategory.objects.create(name="Random ProductCategory")

    def test_string_method(self):
        product_category = ProductCategory.objects.get(pk=1)
        self.assertEqual(str(product_category), product_category.name)


class ProductModelTestcase(TestCase):
    @classmethod
    def setUpTestData(cls):
        ProductCategory.objects.create(name="Random ProductCategory")
        Restaurant.objects.create(
            name="Random restaurant",
            address="Some address",
            contact_phone="+79991234567",
        )
        Product.objects.create(
            name="Random Product",
            category=ProductCategory.objects.get(pk=1),
            price=199.95,
            image="",
            special_status=True,
            description="description",
        )
        RestaurantMenuItem.objects.create(
            restaurant=Restaurant.objects.get(pk=1),
            product=Product.objects.get(pk=1),
            availability=True,
        )
        Product.objects.create(
            name="Random Product 2",
            category=ProductCategory.objects.get(pk=1),
            price=214.09,
            image="",
            special_status=False,
            description="description 2",
        )
        RestaurantMenuItem.objects.create(
            restaurant=Restaurant.objects.get(pk=1),
            product=Product.objects.get(pk=2),
            availability=False,
        )

    def test_string_method(self):
        product = Product.objects.get(id=1)
        self.assertEqual(str(product), product.name)

    def test_available_queryset(self):
        self.assertQuerysetEqual(
            Product.objects.available(), ["<Product: Random Product>"]
        )

    def test_available_queryset_count(self):
        self.assertNotEqual(Product.objects.available().count(), 2)


class RestaurantMenuItemModelTestcase(TestCase):
    @classmethod
    def setUpTestData(cls):
        Restaurant.objects.create(
            name="Random restaurant",
            address="Some address",
            contact_phone="+79991234567",
        )
        ProductCategory.objects.create(name="Random ProductCategory")
        Product.objects.create(
            name="Random Product",
            category=ProductCategory.objects.get(pk=1),
            price=199.95,
            image="",
            special_status=True,
            description="description",
        )
        RestaurantMenuItem.objects.create(
            restaurant=Restaurant.objects.get(pk=1),
            product=Product.objects.get(pk=1),
            availability=False,
        )

    def test_string_method(self):
        restaurant_menu_item = RestaurantMenuItem.objects.get(pk=1)
        expected_string = f"{restaurant_menu_item.restaurant.name} - {restaurant_menu_item.product.name}"
        self.assertEqual(str(restaurant_menu_item), expected_string)
