import razorpay
from django.contrib import messages
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from core import settings
from orders.bag import Bag
from store.models import Order, OrderProduct
from payment.models import PaymentOrder

client = razorpay.Client(auth=(settings.RAZORPAY_ID, settings.RAZORPAY_SECRET_KEY))


def create_payment_order(request):
    amount = int(Bag(request).get_subtotal().__str__())
    if amount < 10:
        messages.error(request, "Total Amount should be greater than or equal to 10!")
        return redirect("orders:summary")
    razorpay_order = client.order.create(
        dict(amount=(amount * 100), currency="INR", payment_capture="0")
    )
    payment_order = PaymentOrder(
        user=request.user,
        payment_order_id=razorpay_order["id"],
        amount=amount,
    )
    payment_order.save()
    callback_url = "paymenthandler/"
    context = {
        "razorpay_order_id": razorpay_order["id"],
        "razorpay_merchant_key": settings.RAZORPAY_ID,
        "razorpay_amount": (amount * 100),
        "currency": "INR",
        "callback_url": callback_url,
    }
    return render(request, "payment/checkout.html", context=context)


# noinspection PyBroadException
@csrf_exempt
def payment_handler(request):
    if request.method == "POST":
        try:
            payment_id = request.POST["razorpay_payment_id"]
            order_id = request.POST["razorpay_order_id"]
            signature = request.POST["razorpay_signature"]
            data = {
                "razorpay_payment_id": payment_id,
                "razorpay_order_id": order_id,
                "razorpay_signature": signature,
            }
            result = client.utility.verify_payment_signature(data)
            if result is not None:
                try:
                    payment_order = PaymentOrder.objects.get(payment_order_id=order_id)
                    client.payment.capture(payment_id, payment_order.amount * 100)
                    order = Order.objects.create(
                        user=request.user,
                        total=payment_order.amount,
                        razorpay_order_id=order_id,
                        address=request.session.get("address"),
                        contact_no=request.session.get("phone"),
                    )
                    payment_order.order = order
                    payment_order.payment_id = payment_id
                    payment_order.signature = signature
                    payment_order.verified = True
                    payment_order.save()
                    bag = Bag(request)
                    print(bag)
                    for item in bag:
                        OrderProduct.objects.create(
                            order=order,
                            product=item["item"],
                            price=item["total_price"],
                            quantity=item["quantity"],
                        )
                    messages.success(request, "Order placed Successfully")
                    return redirect("orders:summary")
                except:
                    messages.error(request, "Order Failed")
            else:
                messages.error(request, "Order Failed. Not verified!!")
            return redirect("orders:summary")
        except:
            return HttpResponseBadRequest()
    else:
        return HttpResponseBadRequest()
