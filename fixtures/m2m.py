# Example code to add variant attributes after loading fixtures

from store.models import Product

product1 = Product.objects.get(pk=1)
product1.tags.add("tshirt", "cotton", "casual")

product2 = Product.objects.get(pk=2)
product2.tags.add("phone", "android", "smartphone")
print("Added tags to Products")
