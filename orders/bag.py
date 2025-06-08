from decimal import Decimal
from core import settings
from store.models import ProductVariant  # <-- use this instead


class Bag:
    def __init__(self, request):
        self.session = request.session
        bag = self.session.get(settings.BAG_SESSION_ID)
        if not bag:
            bag = self.session[settings.BAG_SESSION_ID] = {}
        self.bag = bag

    def add(self, variant, quantity):
        print(variant)
        variant_id = str(variant.id)
        self.bag[variant_id] = {"price": int(variant.price), "quantity": quantity}
        self.save()

    def update(self, variant, quantity):
        variant_id = str(variant.id)
        if variant_id in self.bag:
            self.bag[variant_id]["quantity"] = quantity
            self.save()

    def delete(self, variant):
        variant_id = str(variant.id)
        if variant_id in self.bag:
            del self.bag[variant_id]
            self.save()

    def clear(self):
        if settings.BAG_SESSION_ID in self.session:
            del self.session[settings.BAG_SESSION_ID]
            self.save()

    def __iter__(self):
        variant_ids = self.bag.keys()
        variants = ProductVariant.objects.select_related("product").filter(
            id__in=variant_ids
        )
        bag = self.bag.copy()
        for variant in variants:
            bag[str(variant.id)]["variant"] = variant
        for item in bag.values():
            item["price"] = int(item["price"])
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
