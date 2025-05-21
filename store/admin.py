from django.utils.timezone import now, timedelta
from django.contrib import admin
from django.db import models
from store.models import Product, Category, ProductImage, Order, OrderProduct
from payment.models import PaymentOrder
from unfold.admin import ModelAdmin, StackedInline, TabularInline
from unfold.contrib.forms.widgets import WysiwygWidget
from django.db.models import Sum, Count

# Register your models here.
# admin.py


class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 1  # Number of extra forms to display


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    inlines = [ProductImageInline]
    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        }
    }


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    pass


@admin.register(ProductImage)
class ProductImageAdmin(ModelAdmin):
    pass


class OrderProductInline(StackedInline):
    model = OrderProduct
    extra = 1  # Number of extra forms to display


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    inlines = [OrderProductInline]


@admin.register(PaymentOrder)
class PaymentOrderAdmin(ModelAdmin):
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

    # Top-selling products
    top_products = (
        OrderProduct.objects.values("product__name")
        .annotate(total_quantity=Sum("quantity"))
        .order_by("-total_quantity")[:5]
    )

    # Category distribution
    category_data = Category.objects.annotate(product_count=Count("product")).values(
        "name", "product_count"
    )

    # Recent orders
    recent_orders = Order.objects.select_related("user").order_by("-created_on")[:10]

    # Update context
    context.update(
        {
            "total_revenue": total_revenue,
            "todays_revenue": todays_revenue,
            "dates": [d.strftime("%b %d") for d in dates],
            "orders_per_day": orders_per_day,
            "top_product_names": [item["product__name"] for item in top_products],
            "top_product_quantities": [item["total_quantity"] for item in top_products],
            "category_labels": [item["name"] for item in category_data],
            "category_counts": [item["product_count"] for item in category_data],
            "recent_orders": recent_orders,
        }
    )

    return context
