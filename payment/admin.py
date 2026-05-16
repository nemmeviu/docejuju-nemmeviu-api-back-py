from django.contrib import admin

from .models import PaymentConfig


@admin.register(PaymentConfig)
class PaymentConfigAdmin(admin.ModelAdmin):
    fields = ("qrcode", "pix_code")
