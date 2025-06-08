from django.db import models
from django.forms import ValidationError

# Create your models here.
"""This file contains the store models like product, category,etc. """

import os
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from taggit.managers import TaggableManager
from accounts.models import User
from uuid import uuid4
from thumbnails.fields import ImageField
from phonenumber_field.modelfields import PhoneNumberField


def path_and_rename(instance, filename):
    upload_to = "products/"
    ext = filename.split(".")[-1]
    # get filename
    if instance.pk:
        filename = "{}.{}".format(instance.pk, ext)
    else:
        # set filename as random string
        filename = "{}.{}".format(uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join(upload_to, filename)


class ProductAttribute(models.Model):
    name = models.CharField(max_length=50, unique=True)  # e.g. Size, Color, RAM
    objects = models.Manager()

    def __str__(self):
        return self.name


class ProductAttributeValue(models.Model):
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE)
    value = models.CharField(max_length=50)  # e.g. M, Red, 6GB, 128GB
    objects = models.Manager()

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class Category(models.Model):
    """Category model for categorizing products"""

    cover = ImageField(upload_to="covers/", null=True, blank=True)
    name = models.CharField(max_length=80)
    description = models.TextField()
    slug = models.SlugField(blank=False, unique=True, max_length=80)
    objects = models.Manager()

    class Meta:
        """Extra information about the model"""

        verbose_name_plural = "Categories"

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        """
        This method returns the URL of a particular object
        """
        return reverse("store:show-category", args=[self.slug])


class Product(models.Model):
    """Product model"""

    name = models.CharField(max_length=30)
    description = models.TextField()
    slug = models.SlugField(blank=False, unique=True, max_length=30)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.IntegerField()
    date_added = models.DateField(auto_now_add=True)
    is_available = models.BooleanField(default=True)
    cover = ImageField(upload_to=path_and_rename, null=True, blank=True)
    tags = TaggableManager()
    objects = models.Manager()

    class Meta:
        """Meta class for extra information"""

        ordering = ["-date_added"]

    def __str__(self) -> str:
        return str(self.name)

    def get_absolute_url(self):
        """
        This method returns the URL of a particular object
        """
        return reverse("store:show-product", args=[self.slug])


class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="variants"
    )
    attributes = models.ManyToManyField(
        ProductAttributeValue, related_name="attributes"
    )
    sku = models.CharField(max_length=50, unique=True)  # Stock Keeping Unit
    price = models.IntegerField()
    stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    objects = models.Manager()

    def __str__(self):
        return f"{self.product.name}"


class ProductVariantImage(models.Model):
    """Product image to store image information"""

    image = models.ImageField(upload_to="variants/")
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE, related_name="images"
    )
    alt_text = models.CharField(max_length=100, blank=True)
    objects = models.Manager()

    def __str__(self):
        return str(self.image.url)


class Discount(models.Model):
    """Discount model for discounts"""

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    percentage = models.FloatField()
    name = models.CharField(max_length=20, unique=True)
    valid_till = models.DateField()
    objects = models.Manager()


class ORDER_STATUS(models.TextChoices):
    PLACED = ("PLACED", "Placed")
    COMPLETED = ("COMPLETED", "Completed")
    CANCELLED = ("CANCELLED", "Cancelled")


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10, choices=ORDER_STATUS.choices, default=ORDER_STATUS.PLACED
    )
    contact_no = PhoneNumberField()
    address = models.TextField()
    total = models.PositiveIntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    razorpay_order_id = models.CharField(max_length=22, unique=True)
    objects = models.Manager()

    def __str__(self) -> str:
        return f"Order by :{self.user} createdon:{self.created_on} total:{self.total} status:{self.status}"

    class Meta:
        ordering = ["-created_on"]


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()
    price = models.IntegerField()
    objects = models.Manager()

    def __str__(self) -> str:
        return f"Item:{self.product.product.name} qnty:{self.quantity}"


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.SmallIntegerField(
        validators=[MaxValueValidator(5), MinValueValidator(0)]
    )
    review = models.TextField()
    objects = models.Manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "product"], name="unique rating")
        ]
