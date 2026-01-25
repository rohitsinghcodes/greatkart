from django.shortcuts import render, get_object_or_404
from store.models import Product, ProductVariation
from category.models import Category
from carts.models import CartItem
from django.core.paginator import Paginator
from django.db.models import Q
from collections import defaultdict
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def store(request, category_slug=None):
    products = None

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category, is_available=True)
    else:
        products = Product.objects.filter(is_available=True)

    total_products = products.count()

    paginator = Paginator(products, 6)
    page = request.GET.get('page')
    page_products = paginator.get_page(page)

    context = {
        'products': page_products,
        'total_products': total_products,
    }

    return render(request, 'store/store.html', context)


@login_required(login_url='login')
def product_detail(request, category_slug, product_slug):
    single_product = get_object_or_404(
        Product,
        category__slug=category_slug,
        slug=product_slug,
        is_available=True
    )

    variations = ProductVariation.objects.filter(
        product=single_product,
        is_active=True,
        stock__gt=0
    )

    color_size_map = defaultdict(list)
    all_sizes = set()

    for v in variations:
        color_size_map[v.color].append(v.size)
        all_sizes.add(v.size)

    context = {
        'single_product': single_product,
        'color_size_map': dict(color_size_map),
        'all_sizes': sorted(all_sizes),
    }

    return render(request, 'store/product_detail.html', context)


@login_required(login_url='login')
def search(request):
    keyword = request.GET.get('keyword')
    products = Product.objects.none()

    if keyword:
        products = Product.objects.filter(
            Q(product_name__icontains=keyword) |
            Q(description__icontains=keyword),
            is_available=True
        ).order_by('-created_date')

    total_products = products.count()

    paginator = Paginator(products, 6)
    page = request.GET.get('page')
    page_products = paginator.get_page(page)

    context = {
        'products': page_products,
        'total_products': total_products,
        'keyword': keyword,
    }

    return render(request, 'store/store.html', context)
