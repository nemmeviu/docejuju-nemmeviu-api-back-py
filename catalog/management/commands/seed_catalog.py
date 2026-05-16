from decimal import Decimal

from django.core.management.base import BaseCommand

from catalog.models import Product

# Mesmos ids e dados do front (docejuju-nemmeviu-front-csr-js/src/data/products.js)
SEED = [
    {
        "slug": "brigadeiro-12",
        "name": "Brigadeiro belga",
        "description": "Caixa com 12 unidades. Chocolate belga e granulado.",
        "price": Decimal("42.90"),
        "category": "caixas",
        "emoji": "🍫",
        "accent": "#5c3d2e",
    },
    {
        "slug": "beijinho-12",
        "name": "Beijinho premium",
        "description": "Coco flocado e leite condensado artesanal. 12 un.",
        "price": Decimal("38.90"),
        "category": "caixas",
        "emoji": "🥥",
        "accent": "#8b7355",
    },
    {
        "slug": "cone-trufado",
        "name": "Cone trufado",
        "description": "Cone crocante recheado com ganache. Unidade.",
        "price": Decimal("14.50"),
        "category": "unitarios",
        "emoji": "🍦",
        "accent": "#c45c6a",
    },
    {
        "slug": "brownie",
        "name": "Brownie com nozes",
        "description": "Fatia generosa, chocolate meio amargo.",
        "price": Decimal("18.00"),
        "category": "bolos",
        "emoji": "🟫",
        "accent": "#6b4423",
    },
    {
        "slug": "torta-limao",
        "name": "Torta de limão (fatia)",
        "description": "Massa amanteigada e merengue leve.",
        "price": Decimal("22.00"),
        "category": "bolos",
        "emoji": "🍋",
        "accent": "#d4a017",
    },
    {
        "slug": "alfajor-6",
        "name": "Caixa de alfajores",
        "description": "6 unidades, doce de leite caseiro e coco.",
        "price": Decimal("48.00"),
        "category": "caixas",
        "emoji": "🍪",
        "accent": "#a67c52",
    },
]


class Command(BaseCommand):
    help = "Cria ou atualiza produtos iniciais (idempotente)."

    def handle(self, *args, **options):
        for row in SEED:
            slug = row["slug"]
            defaults = {k: v for k, v in row.items() if k != "slug"}
            defaults["is_active"] = True
            Product.objects.update_or_create(slug=slug, defaults=defaults)
        self.stdout.write(self.style.SUCCESS(f"{len(SEED)} produtos no catálogo."))
