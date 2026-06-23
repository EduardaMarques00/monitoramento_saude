from rest_framework import viewsets
from .models import Prescricao
from .serializers import PrescricaoSerializer

class PrescricaoViewSet(viewsets.ModelViewSet):
    queryset = Prescricao.objects.all()
    serializer_class = PrescricaoSerializer
