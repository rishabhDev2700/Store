from django import forms
from store.models import ProductAttributeValue, ProductVariant, Rating


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ["rating", "review", "product", "user"]
        widgets = {
            "rating": forms.TextInput(
                attrs={
                    "type": "range",
                    "min": "0",
                    "max": "5",
                    "list": "rating",
                }
            ),
            "product": forms.TextInput(attrs={"readonly": "true"}),
            "user": forms.TextInput(attrs={"hidden": "true"}),
        }


# class ProductVariantForm(forms.ModelForm):
#     class Meta:
#         model = ProductVariant
#         fields = "__all__"


class ProductVariantForm(forms.ModelForm):
    attributes = forms.ModelMultipleChoiceField(
        queryset=ProductAttributeValue.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = ProductVariant
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get("product")
        attributes = cleaned_data.get("attributes")

        if not product or not attributes:
            return cleaned_data

        existing_variants = ProductVariant.objects.filter(product=product)
        attr_ids = set(attr.id for attr in attributes)

        for variant in existing_variants:
            if variant.pk == self.instance.pk:
                continue
            variant_attr_ids = set(variant.attributes.values_list("id", flat=True))
            if attr_ids == variant_attr_ids:
                raise forms.ValidationError(
                    "This variant already exists with the same attributes."
                )

        return cleaned_data
