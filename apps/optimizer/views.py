from rest_framework import generics
from rest_framework.response import Response

from apps.optimizer.serializers import OptimizerInputSerialzer
from apps.optimizer.algo import optimize_index


class OptimizeView(generics.CreateAPIView):
    serializer_class = OptimizerInputSerialzer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        output = optimize_index(serializer.validated_data)
        return Response(output)
