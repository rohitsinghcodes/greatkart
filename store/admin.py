from django.contrib import admin
from .models import Product, ProductVariation


# ---------------- PRODUCT ADMIN ----------------
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'product_name',
        'price',
        'is_available',
        'category',
        'created_date',
        'modified_date'
    )
    prepopulated_fields = {'slug': ('product_name',)}
    readonly_fields = ('created_date', 'modified_date')


# ---------------- PRODUCT VARIATION ADMIN ----------------
class ProductVariationAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'color',
        'size',
        'stock',
        'is_active'
    )
    list_filter = ('product', 'color', 'size', 'is_active')
    search_fields = ('product__product_name', 'color', 'size')


# ---------------- REGISTER ----------------
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductVariation, ProductVariationAdmin)
