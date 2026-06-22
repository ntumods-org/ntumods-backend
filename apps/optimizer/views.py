from rest_framework import generics
from rest_framework.response import Response

from apps.optimizer.algo import optimize_index
from apps.optimizer.serializers import OptimizerInputSerialzer


class OptimizeView(generics.CreateAPIView):
    serializer_class = OptimizerInputSerialzer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        output = optimize_index(serializer.validated_data)
        # Always return a JSON list so the response body is not empty.
        return Response(output if output is not None else [])
