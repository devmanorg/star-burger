from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import phonenumbers
from .models import Order, OrderLine, Product


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
    order_keys = ['firstname', 'lastname', 'phonenumber', 'address']
    valid_keys = {}
    data = request.data
    for order_key in order_keys:
        try:
            valid_keys[order_key] = data[order_key]
        except KeyError:
            return Response(
                data={'error': f'{order_key} key is not presented in data'},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )  
    for order_key in order_keys:
        if not isinstance(valid_keys[order_key], str):
            return Response(
                data={'error': f'{order_key} is not str'},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )
    for order_key in order_keys:
        if valid_keys[order_key] is None:
            return Response(
                data={'error': f'{order_key} can not be null'},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )
    try:
        number = phonenumbers.parse(valid_keys['phonenumber'], "RU")
    except:
        return Response(
                data={'error': 'missing phone number'},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )
    if not phonenumbers.is_valid_number(number):
        return Response(
                data={'error': 'Incorrect phone number'},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )
    new_order = Order.objects.create(
        first_name=valid_keys['firstname'],
        last_name=valid_keys['lastname'],
        phone=number,
        address=valid_keys['address']
    )
    try:
        products = data['products']
    except KeyError:
        return Response(
            data={'error': 'Products is not presented in data'},
            status=status.HTTP_406_NOT_ACCEPTABLE,
        )
    if products is None:
        return Response(
            data={'error': 'Products list can not be null'},
            status=status.HTTP_406_NOT_ACCEPTABLE,
        )
    if not isinstance(products, list):
        return Response(
            data={'error': 'Products is not list'},
            status=status.HTTP_406_NOT_ACCEPTABLE,
        )      
    if not len(products):
        return Response(
            data={'error': 'Products list can not be empty'},
            status=status.HTTP_406_NOT_ACCEPTABLE,
        )
    for order_line in data['products']:
        if not Product.objects.filter(id=order_line['product']):
            return Response(
                data={'error': f'Products id={order_line["product"]} is not exist'},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )
    for order_line in data['products']:
        OrderLine.objects.create(
            order=new_order,
            product=Product.objects.get(id=order_line['product']),
            quntity=order_line['quantity']
        )

    return JsonResponse({})
