from django.db import models


class Product(models.Model):
    """Identificador público = slug (ex.: brigadeiro-12), alinhado ao front."""

    slug = models.SlugField(max_length=64, primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=64, blank=True)
    emoji = models.CharField(max_length=8, blank=True)
    accent = models.CharField(
        max_length=16,
        blank=True,
        help_text="Cor hex opcional para o front (ex.: #5c3d2e).",
    )
    image = models.ImageField(upload_to="products/", blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class DiscountRule(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="discount_rules"
    )
    min_quantity = models.PositiveIntegerField(
        help_text="Quantidade mínima para ativar o desconto."
    )
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Percentual de desconto (ex.: 10.00 = 10% de desconto).",
    )

    class Meta:
        ordering = ["product", "min_quantity"]
        unique_together = ["product", "min_quantity"]

    def __str__(self) -> str:
        return f"{self.product.name} — {self.min_quantity}+ ({self.discount_percent}%)"
