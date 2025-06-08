from django.urls import path

from payment import views

app_name = "payment"
urlpatterns = [
    path("", views.create_payment_order, name="create_payment"),
    path("paymenthandler/", views.payment_handler, name="payment_handler"),
    path("order-cancel/", views.cancel_order, name="cancel_order"),
]
