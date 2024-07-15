from decimal import Decimal

from core import settings
from store.models import Product as Item


class Bag:
    def __init__(self, request):
        self.session = request.session
        bag = self.session.get(settings.BAG_SESSION_ID)
        if settings.BAG_SESSION_ID not in request.session:
            bag = self.session[settings.BAG_SESSION_ID] = {}
        self.bag = bag

    def add(self, item, quantity):
        item_id = str(item.id)
        if item_id in self.bag:
            self.bag[item_id]["quantity"] = quantity
        else:
            self.bag[item_id] = {"price": str(item.price), "quantity": quantity}
        self.save()

    def update(self, item, quantity):
        item_id = str(item.id)
        if item_id in self.bag:
            self.bag[item_id]["quantity"] = quantity
        self.save()

    def delete(self, item):
        item_id = str(item.id)
        if item_id in self.bag:
            del self.bag[item_id]
            self.save()

    def clear(self):
        del self.session[settings.BAG_SESSION_ID]

    def __iter__(self):
        item_ids = self.bag.keys()
        items = Item.objects.filter(id__in=item_ids)
        bag = self.bag.copy()
        for item in items:
            bag[str(item.id)]["item"] = item
        for item in bag.values():
            item["price"] = Decimal(item["price"])
            item["total_price"] = item["price"] * item["quantity"]
            yield item

    def __len__(self):
        return sum(item["quantity"] for item in self.bag.values())

    def get_subtotal(self):
        return sum(
            Decimal(item["price"]) * item["quantity"] for item in self.bag.values()
        )

    def save(self):
        self.session.modified = True
