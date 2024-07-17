from django.db import models

# Create your models here.
"""This file contains the store models like product, category,etc. """

import os
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from taggit.managers import TaggableManager
from accounts.models import User
from uuid import uuid4


# Create your models here.
class Category(models.Model):
    """Category model for categorizing products"""

    cover = models.ImageField(upload_to="covers/")
    name = models.CharField(max_length=80)
    description = models.TextField()
    slug = models.SlugField(blank=False, unique=True, max_length=30)
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


class Product(models.Model):
    """Product model"""

    name = models.CharField(max_length=30)
    description = models.TextField()
    slug = models.SlugField(blank=False, unique=True, max_length=30)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.PositiveIntegerField()
    date_added = models.DateField(auto_now=True)
    is_available = models.BooleanField(default=True)
    cover = models.ImageField(upload_to=path_and_rename, null=True)
    thumbnail = models.ImageField(upload_to=path_and_rename, null=True)
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


class ProductImage(models.Model):
    """Product image to store image information"""

    name = models.CharField(max_length=40)
    image = models.ImageField(upload_to="media/")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    objects = models.Manager()

    def __str__(self):
        return str(self.name)


class Discount(models.Model):
    """Discount model for discounts"""

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    percentage = models.FloatField()
    name = models.CharField(max_length=20, unique=True)
    valid_till = models.DateField()
    objects = models.Manager()


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    total = models.PositiveIntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    razorpay_order_id = models.CharField(max_length=22, unique=True)
    objects = models.Manager()

    def __str__(self) -> str:
        return f"Order by :{self.user} createdon:{self.created_on} total:{self.total} completed:{self.is_completed}"

    class Meta:
        ordering = ["-created_on"]


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()
    price = models.PositiveIntegerField()
    objects = models.Manager()

    def __str__(self) -> str:
        return f"Item:{self.item.name} qnty:{self.quantity}"


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
