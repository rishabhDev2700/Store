from django.contrib import admin

from store.models import Product, Category, ProductImage

# Register your models here.
# admin.py

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Number of extra forms to display


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]


admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
admin.site.register(ProductImage)
