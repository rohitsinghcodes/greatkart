from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, ProductVariation
from .models import Cart, CartItem
from django.db.models import Q, Count
from django.http import HttpResponseBadRequest, JsonResponse
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def add_cart(request, product_id):
    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid request")

    product = get_object_or_404(Product, id=product_id)

    # ✅ Get or create cart for logged-in user
    cart, _ = Cart.objects.get_or_create(user=request.user)

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

    # ✅ Get existing cart items for same product
    cart_items = CartItem.objects.filter(
        cart=cart,
        product=product,
        user=request.user
    )

    for item in cart_items:
        if list(item.variations.all()) == [variation]:
            item.quantity += 1
            item.save()
            return redirect('cart')

    # ✅ Create new cart item
    cart_item = CartItem.objects.create(
        product=product,
        cart=cart,
        user=request.user,
        quantity=1
    )
    cart_item.variations.add(variation)

    return redirect('cart')


@login_required(login_url='login')
def remove_cart_item(request, cart_item_id):
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(
        CartItem,
        id=cart_item_id,
        cart=cart,
        user=request.user
    )
    cart_item.delete()
    return redirect('cart')


@login_required(login_url='login')
def remove_cart(request, cart_item_id):
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(
        CartItem,
        id=cart_item_id,
        cart=cart,
        user=request.user
    )

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('cart')


@login_required(login_url='login')
def cart(request):
    total = 0
    quantity = 0

    cart = Cart.objects.filter(user=request.user).first()
    cart_items = CartItem.objects.filter(cart=cart, user=request.user) if cart else []

    for item in cart_items:
        total += item.product.price * item.quantity
        quantity += item.quantity

    tax = (2 * total) / 100
    grand_total = total + tax

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }

    return render(request, 'store/cart.html', context) 


@login_required(login_url='login')
def check_cart_variation(request):
    product_id = request.GET.get('product_id')
    color = request.GET.get('color')
    size = request.GET.get('size')

    if not product_id or not color or not size:
        return JsonResponse({'in_cart': False})

    cart = Cart.objects.filter(user=request.user).first()

    if not cart:
        return JsonResponse({'in_cart': False})

    exists = CartItem.objects.filter(
        cart=cart,
        user=request.user,
        product_id=product_id,
        variations__color__iexact=color,
        variations__size__iexact=size,
    ).exists()

    return JsonResponse({'in_cart': exists})
