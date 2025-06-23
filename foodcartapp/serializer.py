from rest_framework.serializers import ModelSerializer
from foodcartapp.models import Order, OrderItem

from restaurateur.utils import fetch_coordinates


class OrderItemSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = OrderItemSerializer(many=True, allow_empty=False, source='items')

    class Meta:
        model = Order
        fields = [
            'firstname',
            'lastname',
            'address',
            'phonenumber',
            'products'
        ]

    def create(self, validated_data):
        products_items = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        order_items = [
            OrderItem(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price_at_order=item['product'].price * item['quantity']
            ) for item in products_items
        ]
        OrderItem.objects.bulk_create(order_items)
        fetch_coordinates(order.address)
        return order
