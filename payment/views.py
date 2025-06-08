import razorpay
from django.contrib import messages
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from core import settings
from orders.bag import Bag
from store.models import ORDER_STATUS, Order, OrderProduct
from payment.models import PaymentOrder
import logging

client = razorpay.Client(auth=(settings.RAZORPAY_ID, settings.RAZORPAY_SECRET_KEY))
logger = logging.getLogger(__name__)


@login_required
def create_payment_order(request):
    amount = Bag(request).get_subtotal()
    if amount < 10:
        messages.error(request, "Total Amount should be greater than or equal to 10!")
        return redirect("orders:summary")
    print(f"Amount : {amount*100}")
    razorpay_order = client.order.create(
        dict(amount=int(amount * 100), currency="INR", payment_capture="0")
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
                    print(request.session[settings.BAG_SESSION_ID])
                    for item in bag:
                        OrderProduct.objects.create(
                            order=order,
                            product=item["variant"],
                            price=item["price"],
                            quantity=item["quantity"],
                        )
                    messages.success(request, "Order placed Successfully")
                    bag.clear()
                    return redirect("orders:summary")
                except Exception as e:
                    messages.error(request, f"Order Failed {e}")
            else:
                messages.error(request, "Order Failed. Not verified!!")
            return redirect("orders:view_orders")
        except:
            return HttpResponseBadRequest()
    else:
        return HttpResponseBadRequest()


@login_required
def cancel_order(request):
    if request.method == "POST":
        try:
            print("Cancelling Order!")
            order_id = request.POST["order_id"]
            order = get_object_or_404(
                Order,
                pk=order_id,
                user=request.user,
                status=ORDER_STATUS.PLACED,
            )
            print(f"Order Amount:{order.total}")
            payment_order = get_object_or_404(
                PaymentOrder,
                order=order,
                payment_order_id=order.razorpay_order_id,
                user=request.user,
            )
            print(f"payment_order: {payment_order}")
            res = client.payment.refund(
                payment_order.payment_id,
                {
                    "amount": int(order.total * 80),
                    "notes": {
                        "order_id": order.id,
                        "total_amount": order.total,
                        "email": request.user.email,
                    },
                },
            )
            print(res)
            if res["status"] == "processed":
                order.status = ORDER_STATUS.CANCELLED
                order.save()
                messages.success(request, "Your refund request has been processed")
        except Exception as e:
            logger.error(e)
        return redirect("orders:view_orders")
    else:
        raise HttpResponseBadRequest("Method not allowed")
