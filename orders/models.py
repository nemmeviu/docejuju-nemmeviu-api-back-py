import uuid

from django.db import models


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_name = models.CharField(max_length=200)
    customer_phone = models.CharField(max_length=40)
    customer_casa = models.TextField(blank=True, help_text="Número ou identificação da casa.")
    delivery = models.CharField(
        max_length=10,
        choices=[("retirada", "Retirar no local"), ("entrega", "Entregar em casa")],
        default="retirada",
    )
    payment = models.CharField(
        max_length=10,
        choices=[("presencial", "Presencial"), ("pix", "PIX")],
        default="presencial",
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    telegram_sent = models.BooleanField(default=False)
    telegram_error = models.TextField(blank=True)
    email_sent = models.BooleanField(default=False)
    email_error = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Pedido {self.id} — {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.PROTECT,
    )
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Preço unitário no momento do pedido.",
    )

    class Meta:
        ordering = ["id"]

    @property
    def line_total(self):
        return self.unit_price * self.quantity


class TelegramConfig(models.Model):
    bot_token = models.CharField(
        max_length=200,
        help_text="Token do bot Telegram (ex.: 123456:ABC-DEF…).",
    )
    chat_id = models.CharField(
        max_length=80,
        help_text="ID do chat/grupo para onde as notificações serão enviadas.",
    )
    is_enabled = models.BooleanField(
        default=True,
        help_text="Desative para pular notificações sem remover as credenciais.",
    )

    class Meta:
        verbose_name = "Configuração do Telegram"
        verbose_name_plural = "Configuração do Telegram"

    def __str__(self) -> str:
        return f"Telegram: chat {self.chat_id}"


class EmailConfig(models.Model):
    host = models.CharField(max_length=200, default="smtp.gmail.com")
    port = models.PositiveIntegerField(default=587)
    username = models.CharField(max_length=200, help_text="E-mail da conta SMTP.")
    password = models.CharField(max_length=200, help_text="Senha ou app-password SMTP.")
    from_email = models.EmailField(
        help_text="Remetente (geralmente igual ao username)."
    )
    to_email = models.CharField(
        max_length=500,
        help_text="Destinatário(s). Separe múltiplos com vírgula.",
    )
    is_enabled = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Configuração de E-mail"
        verbose_name_plural = "Configuração de E-mail"

    def __str__(self) -> str:
        return f"E-mail: {self.to_email}"
