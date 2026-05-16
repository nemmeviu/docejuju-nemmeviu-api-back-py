from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from catalog.models import Product

from .models import Order, OrderItem
from .email import send_order_email
from .telegram import send_order_to_telegram


class CustomerSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    phone = serializers.CharField(max_length=40)
    delivery = serializers.ChoiceField(
        choices=["retirada", "entrega"], default="retirada"
    )
    payment = serializers.ChoiceField(
        choices=["presencial", "pix"], default="presencial"
    )
    casa = serializers.CharField(required=False, allow_blank=True, default="")


class OrderItemInputSerializer(serializers.Serializer):
    productId = serializers.CharField(max_length=64)
    quantity = serializers.IntegerField(min_value=1)
    name = serializers.CharField(required=False, allow_blank=True)
    unitPrice = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
    )


class OrderCreateSerializer(serializers.Serializer):
    customer = CustomerSerializer()
    items = OrderItemInputSerializer(many=True)
    notes = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Inclua pelo menos um item.")
        return value

    def create(self, validated_data):
        customer = validated_data["customer"]
        items_in = validated_data["items"]
        notes = validated_data.get("notes") or ""

        with transaction.atomic():
            order = Order.objects.create(
                customer_name=customer["name"].strip(),
                customer_phone=customer["phone"].strip(),
                delivery=customer.get("delivery", "retirada"),
                payment=customer.get("payment", "presencial"),
                customer_casa=(customer.get("casa") or "").strip(),
                notes=notes.strip(),
            )
            for row in items_in:
                slug = row["productId"].strip()
                try:
                    product = Product.objects.get(slug=slug, is_active=True)
                except Product.DoesNotExist as exc:
                    raise serializers.ValidationError(
                        {"items": f'Produto "{slug}" não encontrado ou inativo.'}
                    ) from exc
                qty = row["quantity"]
                unit = product.price
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=qty,
                    unit_price=unit,
                )

        try:
            send_order_to_telegram(order)
            order.telegram_sent = True
            order.telegram_error = ""
            order.save(update_fields=["telegram_sent", "telegram_error"])
        except Exception:
            order.telegram_error = "Falha ao notificar Telegram (ver logs)."
            order.save(update_fields=["telegram_error"])

        try:
            send_order_email(order)
            order.email_sent = True
            order.email_error = ""
            order.save(update_fields=["email_sent", "email_error"])
        except Exception:
            order.email_error = "Falha ao enviar e-mail (ver logs)."
            order.save(update_fields=["email_error"])

        return order
