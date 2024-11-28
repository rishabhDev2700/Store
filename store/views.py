from django.shortcuts import render, get_object_or_404
from django.shortcuts import render

# Create your views here.
"""This file contains all view functions related to store"""

from django.shortcuts import redirect, render, get_object_or_404
from store.forms import RatingForm
from store.models import Category, Product, ProductImage, Rating
from django.db.models import Prefetch
from django.core.paginator import Paginator
from django.contrib.postgres.search import SearchVector
from taggit.models import Tag

# Create your views here.


def homepage(request):
    """
    Home page of the website
    """
    categories = Category.objects.all()
    new_arrivals = Product.objects.all()[:10]
    tags = Tag.objects.all()
    context = {"products": new_arrivals, "tags": tags, "categories": categories}

    return render(request, "store/home.html", context=context)


def explore(request):
    """
    Explore page of the website
    """
    categories = Category.objects.all()
    tags = Tag.objects.all()
    return render(
        request, "store/explore.html", context={"categories": categories, "tags": tags}
    )


def list_all(request):
    """
    Shows all products available
    """
    # todo: add pagination
    products = Product.objects.filter(is_available=True)
    paginator = Paginator(products, 8)
    page_number = request.GET.get("page")
    tags = Tag.objects.all()
    page = paginator.get_page(page_number)
    context = {"products": page}
    return render(request, "store/list-all.html", context=context)


def show_product(request, slug):
    """Show a particular product"""
    product = get_object_or_404(Product, slug=slug)
    reviews = Rating.objects.filter(product=product)[:5]
    categories = Category.objects.all()
    tags = Tag.objects.all()
    reviews = Rating.objects.filter(product=product)[0:5]
    images = ProductImage.objects.filter(product=product)
    context = {
        "product": product,
        "reviews": reviews,
        "categories": categories,
        "tags": tags,
        "reviews": reviews,
        "images": images,
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
    # search_result = Product.objects.annotate(
    #     search=SearchVector("name", "description", "slug")
    # ).filter(search=query)
    search_result = Product.objects.filter(name__startswith=query)
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
