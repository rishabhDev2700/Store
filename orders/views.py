from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404

from orders.bag import Bag
from store.models import Order, OrderProduct
from store.models import Product as Item


# Create your views here.
def bag_summary(request):
    bag = Bag(request)
    context = {"bag": bag, "quantity": bag.__len__()}
    return render(request, "orders/bag_summary.html", context=context)


def bag_add(request):
    bag = Bag(request)
    if request.POST.get("action") == "post":
        print(request.POST)
        item_id = int(request.POST.get("item_id"))
        quantity = int(request.POST.get("quantity"))
        item = get_object_or_404(Item, id=item_id)
        bag.add(item=item, quantity=quantity)
        bag_quantity = bag.__len__()
        response = JsonResponse(
            {"quantity": bag_quantity, "message": f"{item.name} added"}
        )
        return response


def bag_delete(request):
    bag = Bag(request)
    if request.POST.get("action") == "post":
        item_id = int(request.POST.get("item_id"))
        item = get_object_or_404(Item, id=item_id)
        bag.delete(item=item)
        bag_quantity = bag.__len__()
        bag_subtotal = bag.get_subtotal()
        response = JsonResponse(
            {
                "quantity": bag_quantity,
                "subtotal": bag_subtotal,
                "message": f"{item.name} removed",
            }
        )
        return response


def bag_update(request):
    bag = Bag(request)
    if request.POST.get("action") == "post":
        item_id = int(request.POST.get("item_id"))
        quantity = int(request.POST.get("quantity"))
        item = get_object_or_404(Item, id=item_id)
        bag.update(item=item, quantity=quantity)
        bag_quantity = bag.__len__()
        bag_subtotal = bag.get_subtotal()
        response = JsonResponse(
            {
                "quantity": bag_quantity,
                "subtotal": bag_subtotal,
                "message": f"{item.name} updated",
            }
        )
        return response


def bag_clear(request):
    bag = Bag(request)
    bag.clear()
    return JsonResponse({"quantity": 0, "subtotal": 0, "message": "Bag Cleared"})


def view_orders(request):
    all_orders = Order.objects.filter(user=request.user)
    incompleted = all_orders.filter(status="PLACED")
    incompleted_orders = []
    for order in incompleted:
        items = OrderProduct.objects.filter(order=order)
        incompleted_orders.append([order, items])
    completed = all_orders.filter(status="COMPLETED")
    completed_orders = []
    for order in completed:
        items = OrderProduct.objects.filter(order=order)
        completed_orders.append([order, items])
    context = {
        "completed_orders": completed_orders,
        "incompleted_orders": incompleted_orders,
    }
    return render(request, "orders/view_orders.html", context=context)


def save_address(request):
    if request.method == "POST":
        address = request.POST.get("address")
        phone = request.POST.get("phone")

        if not address or not phone:
            return redirect("your_address_form_page")

        request.session["address"] = address
        request.session["phone"] = phone
        return redirect("payment:create_payment")
    return render(request, "orders/order_address.html")
