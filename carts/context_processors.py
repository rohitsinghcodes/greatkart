from .models import Cart, CartItem

def counter(request):
    cart_count = 0

    # Skip admin pages
    if request.path.startswith('/admin'):
        return {'cart_count': cart_count}

    # Only run cart logic for logged-in users
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()

        if cart:
            cart_items = CartItem.objects.filter(cart=cart)
            for item in cart_items:
                cart_count += item.quantity

    return {'cart_count': cart_count}
