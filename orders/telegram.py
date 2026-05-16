import logging
from decimal import Decimal

import requests
from django.conf import settings

from .models import TelegramConfig

logger = logging.getLogger(__name__)


def _telegram_creds():
    config = TelegramConfig.objects.filter(is_enabled=True).first()
    if config:
        return config.bot_token, config.chat_id
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
    chat_id = getattr(settings, "TELEGRAM_CHAT_ID", "")
    return token, chat_id


def format_order_message(order) -> str:
    lines = []
    total = Decimal("0")
    for item in order.items.select_related("product").all():
        lt = item.unit_price * item.quantity
        total += lt
        lines.append(
            f"• {item.quantity}× {item.product.name} — "
            f"R$ {item.unit_price:.2f} (linha: R$ {lt:.2f})"
        )
    items_block = "\n".join(lines) if lines else "(sem itens)"
    addr = order.customer_casa.strip() or "—"
    entrega = dict(order._meta.get_field("delivery").choices).get(order.delivery, order.delivery)
    pagamento = dict(order._meta.get_field("payment").choices).get(order.payment, order.payment)
    notes = order.notes.strip() or "—"
    return (
        f"<b>Novo pedido Doce Juju</b>\n"
        f"<code>{order.id}</code>\n\n"
        f"<b>Cliente</b>\n"
        f"Nome: {order.customer_name}\n"
        f"Telefone: {order.customer_phone}\n"
        f"Entrega: {entrega}\n"
        + (f"Casa: {addr}\n" if order.delivery == "entrega" else "")
        + f"Pagamento: {pagamento}\n\n"
        f"<b>Itens</b>\n{items_block}\n\n"
        f"<b>Total</b> R$ {total:.2f}\n\n"
        f"<b>Observações</b>\n{notes}"
    )


def send_order_to_telegram(order) -> bool:
    token, chat_id = _telegram_creds()
    if not token or not chat_id:
        logger.info("Telegram não configurado; pedido %s gravado sem notificação.", order.id)
        return False

    text = format_order_message(order)
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        r = requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": text[:4000],
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            },
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        if not data.get("ok"):
            raise RuntimeError(data.get("description", str(data)))
        return True
    except Exception as exc:
        logger.exception("Falha ao enviar pedido %s ao Telegram: %s", order.id, exc)
        raise
