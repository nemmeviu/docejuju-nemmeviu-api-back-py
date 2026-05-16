from django.db import models


class PaymentConfig(models.Model):
    qrcode = models.ImageField(
        upload_to="payment/",
        help_text="Imagem do QR Code PIX.",
    )
    pix_code = models.CharField(
        max_length=256,
        help_text="Código PIX copia-e-cola (string alfanumérica).",
    )

    class Meta:
        verbose_name = "Configuração de Pagamento"
        verbose_name_plural = "Configuração de Pagamento"

    def __str__(self) -> str:
        return f"PIX: {self.pix_code[:32]}…"
