from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from catalog.views import ProductListView
from orders.views import OrderCreateView
from payment.views import PaymentConfigView

admin.site.site_header = "Doce Juju — administração"
admin.site.site_title = "Doce Juju"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/products/", ProductListView.as_view(), name="api-product-list"),
    path("api/orders/", OrderCreateView.as_view(), name="api-order-create"),
    path("api/payment-config/", PaymentConfigView.as_view(), name="api-payment-config"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
