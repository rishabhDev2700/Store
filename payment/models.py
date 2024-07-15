from django.db import models

from accounts.models import User
from store.models import Order


# Create your models here.
class PaymentOrder(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_order_id = models.CharField(unique=True, max_length=22)
    payment_id = models.CharField(max_length=20, null=True)
    amount = models.PositiveIntegerField(default=0)
    signature = models.CharField(max_length=64, null=True)
    verified = models.BooleanField(default=False)
    time = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
