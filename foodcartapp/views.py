from django.http import JsonResponse
from django.templatetags.static import static
from phonenumber_field.phonenumber import PhoneNumber
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product, Order


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    required_fields = ['products', 'firstname', 'lastname', 'phonenumber', 'address']
    if not all([request.data.get(field) for field in required_fields]):
        return Response(
            {'error': f'missing one or more required fields: {", ".join(required_fields)}'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    required_product_fields = ['product', 'quantity']
    for product in request.data['products']:
        if not all([product.get(field) for field in required_product_fields]):
            return Response(
                {'error': f'each product must have these int fields: {", ".join(required_product_fields)}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    if not isinstance(request.data.get('products'), list):
        return Response(
            {'error': 'products must be a list'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    str_fields = ['firstname', 'lastname', 'phonenumber', 'address']
    if not all([isinstance(request.data[field], str) for field in str_fields]):
        return Response(
            {'error': 'wrong data type for one or more string fields'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not PhoneNumber.from_string(request.data['phonenumber']).is_valid():
        return Response(
            {'error': 'invalid phone number'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    for product in request.data['products']:
        try:
            Product.objects.get(pk=product.get('product'))
        except Product.DoesNotExist:
            return Response(
                {'error': 'product with the specified id does not exist'},
                status=status.HTTP_400_BAD_REQUEST,
            )


    request_products = request.data.pop('products')
    order = Order.objects.create(**request.data)
    for product_order in request_products:
        order.products.add(
            product_order['product'],
            through_defaults={'quantity': product_order['quantity']}
        )

    return Response({
        'order_id': order.id
    })
