import logging
from decimal import Decimal

from django.core.mail import EmailMultiAlternatives
from django.core.mail import get_connection as django_get_connection

from .models import EmailConfig

logger = logging.getLogger(__name__)


def _email_config():
    return EmailConfig.objects.filter(is_enabled=True).first()


def _smtp_connection(config):
    return django_get_connection(
        host=config.host,
        port=config.port,
        username=config.username,
        password=config.password,
        use_tls=config.port == 587,
        use_ssl=config.port == 465,
    )


def _format_order_html(order) -> str:
    lines = []
    total = Decimal("0")
    for item in order.items.select_related("product").all():
        lt = item.unit_price * item.quantity
        total += lt
        lines.append(
            f"<tr>"
            f"<td style='padding:4px 8px'>{item.quantity}× {item.product.name}</td>"
            f"<td style='padding:4px 8px;text-align:right'>R$ {item.unit_price:.2f}</td>"
            f"<td style='padding:4px 8px;text-align:right'>R$ {lt:.2f}</td>"
            f"</tr>"
        )
    items_block = "".join(lines) if lines else "<tr><td colspan='3'>(sem itens)</td></tr>"
    addr = order.customer_casa.strip() or "—"
    entrega = dict(order._meta.get_field("delivery").choices).get(order.delivery, order.delivery)
    pagamento = dict(order._meta.get_field("payment").choices).get(order.payment, order.payment)
    casa_html = f"<br>Casa: {addr}" if order.delivery == "entrega" else ""
    notes = order.notes.strip() or "—"
    return (
        f"<h2>Novo pedido DoceJuju</h2>"
        f"<p><code>{order.id}</code></p>"
        f"<h3>Cliente</h3>"
        f"<p>Nome: {order.customer_name}<br>"
        f"Telefone: {order.customer_phone}<br>"
        f"Entrega: {entrega}{casa_html}<br>"
        f"Pagamento: {pagamento}</p>"
        f"<h3>Itens</h3>"
        f"<table border='1' cellpadding='0' cellspacing='0' style='border-collapse:collapse;width:100%'>"
        f"<thead><tr style='background:#eee'>"
        f"<th style='padding:6px 8px;text-align:left'>Item</th>"
        f"<th style='padding:6px 8px;text-align:right'>Unit.</th>"
        f"<th style='padding:6px 8px;text-align:right'>Total</th>"
        f"</tr></thead>"
        f"<tbody>{items_block}</tbody>"
        f"</table>"
        f"<p><strong>Total: R$ {total:.2f}</strong></p>"
        f"<h3>Observações</h3><p>{notes}</p>"
    )


def send_order_email(order) -> bool:
    config = _email_config()
    if not config:
        logger.info("E-mail não configurado; pedido %s gravado sem notificação.", order.id)
        return False

    subject = f"Novo pedido DoceJuju #{order.id}"
    html = _format_order_html(order)
    to_list = [e.strip() for e in config.to_email.split(",") if e.strip()]

    msg = EmailMultiAlternatives(
        subject=subject,
        body=html,
        from_email=config.from_email,
        to=to_list,
        connection=_smtp_connection(config),
    )
    msg.attach_alternative(html, "text/html")

    try:
        msg.send(fail_silently=False)
        return True
    except Exception as exc:
        logger.exception("Falha ao enviar e-mail do pedido %s: %s", order.id, exc)
        raise
