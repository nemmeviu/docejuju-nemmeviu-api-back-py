from django.contrib import admin

from .models import DiscountRule, Product


class DiscountRuleInline(admin.TabularInline):
    model = DiscountRule
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [DiscountRuleInline]
    list_display = ("slug", "name", "price", "category", "is_active", "image")
    list_filter = ("is_active", "category")
    search_fields = ("slug", "name")


@admin.register(DiscountRule)
class DiscountRuleAdmin(admin.ModelAdmin):
    list_display = ("product", "min_quantity", "discount_percent")
    list_filter = ("product",)
