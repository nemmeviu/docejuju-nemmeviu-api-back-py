from rest_framework import serializers

from .models import DiscountRule, Product


class DiscountRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountRule
        fields = ("min_quantity", "discount_percent")


class ProductSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="slug", read_only=True)
    discount_rules = DiscountRuleSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "description",
            "price",
            "category",
            "emoji",
            "accent",
            "image",
            "discount_rules",
        )
