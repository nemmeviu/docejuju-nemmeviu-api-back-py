from django.contrib import admin

from .models import EmailConfig, Order, OrderItem, TelegramConfig


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "unit_price")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id", "customer_name", "customer_phone", "delivery", "payment", "created_at",
        "telegram_sent", "email_sent",
    )
    list_filter = ("telegram_sent", "email_sent", "created_at")
    search_fields = ("customer_name", "customer_phone", "id")
    readonly_fields = (
        "id", "created_at",
        "telegram_sent", "telegram_error",
        "email_sent", "email_error",
    )
    inlines = [OrderItemInline]


@admin.register(TelegramConfig)
class TelegramConfigAdmin(admin.ModelAdmin):
    fields = ("bot_token", "chat_id", "is_enabled")
    list_display = ("chat_id", "is_enabled")


@admin.register(EmailConfig)
class EmailConfigAdmin(admin.ModelAdmin):
    fields = (
        "host", "port", "username", "password",
        "from_email", "to_email", "is_enabled",
    )
    list_display = ("to_email", "host", "is_enabled")
