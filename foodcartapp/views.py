from typing import OrderedDict
from django.http import JsonResponse
from django.templatetags.static import static
import json
from datetime import datetime
from .models import Order, OrderProduct


from .models import Product


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
            },
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


def register_order(request):    
    try:
        order_data = json.loads(request.body.decode())
        order = Order.objects.create(            
            address=order_data["address"],
            firstname=order_data["firstname"],
            lastname=order_data["lastname"],
            phonenumber=order_data["phonenumber"]
        )

        for i in order_data["products"]:                
            ordered_product = OrderProduct.objects.create(
                product = Product.objects.get(id=int(i["product"])),    
                quantity = int(i["quantity"]),
                order = order
            )
            order.ordered_products.add(ordered_product)                               
        order.save()
        
        return JsonResponse({"id": 1, "message":"Created"})
    except ValueError:
        return JsonResponse({
            'error': 'cannot parse json order',
        })
    
