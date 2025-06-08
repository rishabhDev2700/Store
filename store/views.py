from unicodedata import category
from django.shortcuts import render, get_object_or_404
from django.db.models import Exists, OuterRef, Count, Q
import json
from django.core.serializers.json import DjangoJSONEncoder

# Create your views here.
"""This file contains all view functions related to store"""

from django.shortcuts import redirect, render, get_object_or_404
from store.forms import RatingForm
from store.models import (
    Category,
    Product,
    ProductAttribute,
    ProductAttributeValue,
    ProductVariant,
    Rating,
    ProductVariantImage,
)
from django.core.paginator import Paginator
from django.contrib.postgres.search import SearchVector
from taggit.models import Tag

# Create your views here.


def homepage(request):
    # Get categories for preview
    categories = Category.objects.all()[:4]  # First 4 categories
    tags = Tag.objects.all()
    # Get featured products (latest products as featured)
    featured_products = Product.objects.filter(is_available=True).order_by(
        "-date_added"
    )[:8]

    context = {
        "tags": tags,
        "categories": categories,
        "featured_products": featured_products,
    }

    return render(request, "store/home.html", context)


def explore(request):
    """
    Explore page of the website
    """
    tags = Tag.objects.all()
    categories = Category.objects.annotate(
        product_count=Count("product", filter=Q(product__is_available=True))
    ).order_by("name")

    # Get featured products (you can define this logic - maybe recent or popular ones)
    featured_products = Product.objects.filter(is_available=True).order_by(
        "-date_added"
    )[
        :8
    ]  # Latest 8 products as featured

    # Get all available products
    products = (
        Product.objects.filter(is_available=True)
        .select_related("category")
        .prefetch_related("tags", "variants")
        .order_by("-date_added")
    )

    context = {
        "categories": categories,
        "featured_products": featured_products,
        "products": products,
    }

    return render(request, "store/explore.html", context)


def list_all(request):
    """
    Shows all products that have at least one available variant
    """
    # Filter products that have at least one available variant
    available_variant_subquery = ProductVariant.objects.filter(
        product=OuterRef("pk"),
        is_available=True,
        stock__gt=0,  # Optional: only show if in stock
    )

    products = Product.objects.annotate(
        has_available_variant=Exists(available_variant_subquery)
    ).filter(has_available_variant=True)

    paginator = Paginator(products, 8)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    tags = Tag.objects.all()
    categories = Category.objects.all()

    context = {
        "categories": categories,
        "products": page,
        "tags": tags,
    }
    return render(request, "store/list-all.html", context=context)


def show_product(request, slug):
    """Show a particular product along with its variants and reviews"""
    product = get_object_or_404(Product, slug=slug)

    variants = product.variants.filter(is_available=True, stock__gt=0).prefetch_related(
        "attributes", "images"
    )

    # Optional: extract all attribute types and their values for frontend selectors
    attribute_values = ProductAttributeValue.objects.filter(
        id__in=[attr.id for variant in variants for attr in variant.attributes.all()]
    ).select_related("attribute")

    # Build a dict of attribute name -> set of values
    attribute_options = {}
    for attr_value in attribute_values:
        name = attr_value.attribute.name
        attribute_options.setdefault(name, set()).add(attr_value.value)

    reviews = Rating.objects.filter(product=product)[:5]
    categories = Category.objects.all()
    tags = Tag.objects.all()
    variant_data = []
    for variant in variants:
        variant_data.append(
            {
                "id": variant.id,
                "price": variant.price,
                "attributes": {
                    v.attribute.name: v.value for v in variant.attributes.all()
                },
                "images": [img.image.url for img in variant.images.all()],
            }
        )

    context = {
        "product": product,
        "variants": variants,
        "reviews": reviews,
        "categories": categories,
        "tags": tags,
        "attribute_options": attribute_options,
        # You can also pass the first variant’s images if needed
        "variants_data_json": json.dumps(variant_data, cls=DjangoJSONEncoder),
        "default_images": variants[0].images.all() if variants else [],
    }
    return render(request, "store/single-item.html", context=context)


def list_categories(request):
    """
    Shows the list of categories
    """
    categories = Category.objects.all()
    tags = Tag.objects.all()
    context = {"categories": categories, "tags": tags}
    return render(request, "store/categories.html", context=context)


def show_category(request, slug):
    """Shows all products in the given category"""
    category = get_object_or_404(
        Category.objects.prefetch_related("product_set"), slug=slug
    )
    categories = Category.objects.all()
    products = category.product_set.filter(is_available=True)
    tags = Tag.objects.all()

    context = {
        "category": category,
        "products": products,
        "categories": categories,
        "tags": tags,
    }
    return render(request, "store/list-items.html", context=context)


def list_best_sellers(request):
    """Fetches the bestsellers"""
    return render(request, "store/list-best-sellers.html")


def list_new_arrivals(request):
    """Fetches the new arrivals from the database"""
    return render(request, "store/list-new-arrivals.html")


def landing(request):
    # return render(request, "store/landing_page.html")
    return render(request, "store/home.html")


def review_form(request, id):
    product = Product.objects.get(id=id)
    if request.method == "POST":
        data = request.POST.copy()
        # data.update({"product__id"})
        form = RatingForm(data=data)
        if form.is_valid():
            form.save()
            return redirect("store:show-product", product.slug)
        else:
            return render(request, "store/review-page.html", context={"form": form})
    form = RatingForm(data={"product": product, "user": request.user})
    return render(
        request, "store/review-page.html", context={"form": form, "product": product}
    )


def search_products(request):
    query = request.GET.get("query")
    search_result = Product.objects.annotate(
        search=SearchVector("name", "description", "slug")
    ).filter(search=query)
    # search_result = Product.objects.filter(name__startswith=query)
    tags = Tag.objects.all()
    print(query)
    return render(
        request,
        "store/list-items.html",
        context={
            "products": search_result,
            "tags": tags,
            "category": {"name": "Search results"},
        },
    )


def product_by_tag(request, slug):
    products = Product.objects.filter(tags__slug=slug)
    tags = Tag.objects.all()
    return render(
        request, "store/list-items.html", {"products": products, "tags": tags}
    )


def terms_and_conditions(request):
    return render(request, "store/terms.html")


def privacy(request):
    return render(request, "store/privacy.html")
