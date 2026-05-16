from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from .models import Order
from .serializers import OrderCreateSerializer


class OrderCreateView(CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(
            {
                "id": str(order.id),
                "message": "Pedido registrado com sucesso.",
            },
            status=status.HTTP_201_CREATED,
        )
