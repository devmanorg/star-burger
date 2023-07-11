from rest_framework.serializers import ModelSerializer

from places.models import Location
from .models import Order, ProductOrder


class ProductOrderSerializer(ModelSerializer):
    class Meta:
        model = ProductOrder
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = ProductOrderSerializer(many=True, allow_empty=False, write_only=True)

    class Meta:
        model = Order
        fields = ['firstname', 'lastname', 'phonenumber', 'address', 'products']

    def create(self, validated_data):
        products_in_order = self.validated_data['products']
        order = Order.objects.create(
            firstname=self.validated_data['firstname'],
            lastname=self.validated_data['lastname'],
            phonenumber=self.validated_data['phonenumber'],
            address=self.validated_data['address'],
        )
        for product_order in products_in_order:
            product = product_order['product']
            order.products.add(
                product,
                through_defaults={
                    'quantity': product_order['quantity'],
                    'product_price': product.price,
                }
            )
        Location.update_by_address(order.address)
        return order
