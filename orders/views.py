from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from carts.models import CartItem
from .forms import OrderForm
from .models import Order, OrderProduct
import datetime
from django.http import HttpResponse

@login_required(login_url='login')
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user, is_active=True)

    if not cart_items.exists():
        return redirect('store')

    total = sum(item.product.price * item.quantity for item in cart_items)
    tax = (2 * total) / 100
    grand_total = total + tax

    form = OrderForm()  # GET only

    context = {
        'form': form,
        'total': total,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'orders/checkout.html', context)

@login_required(login_url='login')
def place_order(request):
    cart_items = CartItem.objects.filter(user=request.user, is_active=True)

    if not cart_items.exists():
        return redirect('store')

    # 🔥 STEP 1: Handle billing form POST
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            request.session['order_form'] = form.cleaned_data
            return redirect('place_order')  # PRG pattern
        else:
            return redirect('checkout')

    # 🔥 STEP 2: Handle GET (confirmation page)
    order_data = request.session.get('order_form')
    if not order_data:
        return redirect('checkout')

    total = sum(item.product.price * item.quantity for item in cart_items)
    tax = (2 * total) / 100
    grand_total = total + tax

    context = {
        'order_data': order_data,
        'cart_items': cart_items,
        'total': total,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'orders/place_order.html', context)


@login_required(login_url='login')
def cash_on_delivery(request):
    if request.method != 'POST':
        return redirect('checkout')

    cart_items = CartItem.objects.filter(user=request.user, is_active=True)
    if not cart_items.exists():
        return redirect('store')

    order_data = request.session.get('order_form')
    if not order_data:
        return redirect('checkout')

    form = OrderForm(order_data)

    total = sum(item.product.price * item.quantity for item in cart_items)
    tax = (2 * total) / 100
    grand_total = total + tax

    if form.is_valid():
        # 1️⃣ Save Order
        order = form.save(commit=False)
        order.user = request.user
        order.order_total = grand_total
        order.tax = tax
        order.payment_method = 'COD'
        order.status = 'New'
        order.ip = request.META.get('REMOTE_ADDR')
        order.save()

        order.order_number = datetime.date.today().strftime('%Y%m%d') + str(order.id)
        order.save()

        # 2️⃣ Save Order Products
        for item in cart_items:
            order_product = OrderProduct.objects.create(
                order=order,
                user=request.user,
                product=item.product,
                quantity=item.quantity,
                product_price=item.product.price,
                ordered=True,
            )
            order_product.variations.set(item.variations.all())

        # 3️⃣ Clear Cart
        cart_items.delete()

        # 4️⃣ Store order ID in session for order_complete page
        request.session['last_order_id'] = order.id

        # 5️⃣ Clean order_form session
        del request.session['order_form']

        # 6️⃣ Redirect to order_complete page
        return redirect('order_complete')

    return redirect('checkout')


@login_required(login_url='login')
def paypal_payment_success(request):
    cart_items = CartItem.objects.filter(user=request.user, is_active=True)
    order_data = request.session.get('order_form')

    if not cart_items.exists() or not order_data:
        return redirect('store')

    form = OrderForm(order_data)
    total = sum(item.product.price * item.quantity for item in cart_items)
    tax = (2 * total) / 100
    grand_total = total + tax

    if form.is_valid():
        # 1️⃣ Save payment info
        payment = Payment.objects.create(
            user=request.user,
            payment_method='PayPal',
            amount_paid=grand_total,
            status='COMPLETED',
        )

        # 2️⃣ Save order
        order = form.save(commit=False)
        order.user = request.user
        order.payment = payment
        order.order_total = grand_total
        order.tax = tax
        order.status = 'Completed'
        order.ip = request.META.get('REMOTE_ADDR')
        order.save()
        order.order_number = datetime.date.today().strftime('%Y%m%d') + str(order.id)
        order.save()

        # 3️⃣ Save order products
        for item in cart_items:
            order_product = OrderProduct.objects.create(
                order=order,
                user=request.user,
                product=item.product,
                quantity=item.quantity,
                product_price=item.product.price,
                ordered=True,
            )
            order_product.variations.set(item.variations.all())

        # 4️⃣ Clear cart & session
        cart_items.delete()
        request.session['last_order_id'] = order.id
        del request.session['order_form']

        # 5️⃣ Redirect to order complete
        return redirect('order_complete')

    return redirect('checkout')


@login_required(login_url='login')
def order_complete(request):
    # 1️⃣ Get last order ID from session
    order_id = request.session.get('last_order_id')
    if not order_id:
        return redirect('store')  # fallback

    # 2️⃣ Fetch order and products
    order = Order.objects.get(id=order_id)
    ordered_products = OrderProduct.objects.filter(order=order)

    # 3️⃣ Optional: clear session after displaying
    del request.session['last_order_id']

    context = {
        'order': order,
        'ordered_products': ordered_products,
    }
    return render(request, 'orders/order_complete.html', context)


@login_required(login_url='login')
def my_orders(request):
    status_filter = request.GET.get('status', 'all')  # default = all

    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    if status_filter != 'all':
        orders = orders.filter(status=status_filter)

    status_options = ['all', 'New', 'Accepted', 'Completed', 'Cancelled']

    context = {
        'orders': orders,
        'status_filter': status_filter,
        'status_options': status_options
    }

    return render(request, 'orders/my_orders.html', context)

