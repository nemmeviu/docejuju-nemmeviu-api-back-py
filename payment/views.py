from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PaymentConfig
from .serializers import PaymentConfigSerializer


class PaymentConfigView(APIView):
    def get(self, request):
        config = PaymentConfig.objects.first()
        if not config:
            raise Http404("PIX não configurado.")
        return Response(PaymentConfigSerializer(config).data)
