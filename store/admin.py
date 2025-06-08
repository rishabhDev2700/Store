import json
from django.utils.timezone import now, timedelta
from django.contrib import admin
from django.db import models
from store.forms import ProductVariantForm
from store.models import (
    Product,
    Category,
    Order,
    OrderProduct,
    ProductAttribute,
    ProductAttributeValue,
    ProductVariant,
    ProductVariantImage,
    Rating,
)
from payment.models import PaymentOrder
from unfold.admin import ModelAdmin, StackedInline, TabularInline
from unfold.contrib.forms.widgets import WysiwygWidget
from django.db.models import Sum, Count


# Register your models here.
# admin.py
@admin.register(Product)
class ProductAdmin(ModelAdmin):
    pass


@admin.register(ProductAttribute)
class ProductAttributeAdmin(ModelAdmin):
    pass


@admin.register(ProductAttributeValue)
class ProductAttributeValueAdmin(ModelAdmin):
    pass


class ProductVariantImageInline(TabularInline):
    model = ProductVariantImage
    extra = 1  # Number of extra forms to display


@admin.register(ProductVariant)
class ProductVariantAdmin(ModelAdmin):
    form = ProductVariantForm
    list_display = ["product", "sku", "price", "stock", "is_available"]
    inlines = [ProductVariantImageInline]


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    pass


class OrderProductInline(StackedInline):
    model = OrderProduct
    extra = 1  # Number of extra forms to display


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    inlines = [OrderProductInline]
    list_display = ("id", "user", "status", "total", "created_on")


@admin.register(PaymentOrder)
class PaymentOrderAdmin(ModelAdmin):
    list_display = ("payment_id", "user", "amount", "time", "order__status")
    ordering = ("time",)
    search_fields = ("payment_order_id", "payment_id")


@admin.register(Rating)
class RatingAdmin(ModelAdmin):
    pass


def admin_dashboard(request, context):
    today = now().date()

    # Revenue
    total_revenue = (
        Order.objects.filter(status="COMPLETED").aggregate(total=Sum("total"))["total"]
        or 0
    )
    todays_revenue = (
        Order.objects.filter(status="COMPLETED", created_on__date=today).aggregate(
            total=Sum("total")
        )["total"]
        or 0
    )

    # Orders in last 7 days
    dates = [today - timedelta(days=i) for i in range(6, -1, -1)]
    orders_per_day = [
        Order.objects.filter(created_on__date=day).count() for day in dates
    ]

    # Top-selling products (Fixed the reference)
    top_products = (
        OrderProduct.objects.values("product__product__name")
        .annotate(total_quantity=Sum("quantity"))
        .order_by("-total_quantity")[:5]
    )

    # Category distribution
    category_data = Category.objects.annotate(product_count=Count("product")).values(
        "name", "product_count"
    )

    # Recent orders
    recent_orders = Order.objects.select_related("user").order_by("-created_on")[:10]

    context.update(
        {
            "total_revenue": total_revenue,
            "todays_revenue": todays_revenue,
            "dates": json.dumps([d.strftime("%b %d") for d in dates]),
            "orders_per_day": json.dumps(orders_per_day),
            "top_product_names": json.dumps(
                [item["product__product__name"] for item in top_products]
            ),
            "top_product_quantities": json.dumps(
                [item["total_quantity"] for item in top_products]
            ),
            "category_labels": json.dumps([item["name"] for item in category_data]),
            "category_counts": json.dumps(
                [item["product_count"] for item in category_data]
            ),
            "recent_orders": recent_orders,
        }
    )

    return context
