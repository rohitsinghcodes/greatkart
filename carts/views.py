from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, ProductVariation
from .models import Cart, CartItem
from django.db.models import Q, Count
from django.http import HttpResponseBadRequest, JsonResponse


def cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid request")

    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(cart_id=cart_id(request))

    color = request.POST.get('color')
    size = request.POST.get('size')

    if not color or not size:
        return HttpResponseBadRequest("Color and size required")

    variation = get_object_or_404(
        ProductVariation,
        product=product,
        color=color,
        size=size,
        is_active=True,
        stock__gt=0
    )

    cart_items = CartItem.objects.filter(cart=cart, product=product)

    for item in cart_items:
        if list(item.variations.all()) == [variation]:
            item.quantity += 1
            item.save()
            return redirect('cart')

    cart_item = CartItem.objects.create(
        product=product,
        cart=cart,
        quantity=1
    )
    cart_item.variations.add(variation)
    cart_item.save()

    return redirect('cart')


def remove_cart_item(request, cart_item_id):
    cart = get_object_or_404(Cart, cart_id=cart_id(request))
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart=cart)

    cart_item.delete()
    return redirect('cart')



def remove_cart(request, cart_item_id):
    cart = get_object_or_404(Cart, cart_id=cart_id(request))
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart=cart)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('cart')


def cart(request):
    total = 0
    quantity = 0
    cart_items = []

    try:
        cart = Cart.objects.get(cart_id=cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart)

        for item in cart_items:
            total += item.product.price * item.quantity
            quantity += item.quantity

        tax = (2 * total) / 100
        grand_total = total + tax

    except Cart.DoesNotExist:
        tax = 0
        grand_total = 0

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }

    return render(request, 'store/cart.html', context)



def check_cart_variation(request):
    try:
        product_id = request.GET.get('product_id')
        color = request.GET.get('color')
        size = request.GET.get('size')

        if not product_id or not color or not size:
            return JsonResponse({'in_cart': False})

        cart = Cart.objects.get(cart_id=cart_id(request))

        exists = CartItem.objects.filter(
            cart=cart,
            product_id=product_id,
            variations__color__iexact=color,
            variations__size__iexact=size,
        ).exists()

        return JsonResponse({'in_cart': exists})

    except Exception as e:
        print("CHECK CART ERROR:", e)
        return JsonResponse({'in_cart': False})
