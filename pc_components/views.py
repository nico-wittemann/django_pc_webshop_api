from rest_framework import viewsets
from .models import Component, Pc
from .serializers import ComponentSerializer, PcSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import IsPcOwnerOrCustomizedFalse # Not needed currently


class ComponentViewSet(viewsets.ModelViewSet):
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer
    permission_classes = [AllowAny]
    ordering = ['name']

class PcViewSet(viewsets.ModelViewSet):
    queryset = Pc.objects.all()
    serializer_class = PcSerializer
    permission_classes = [AllowAny]   # IsPcOwnerOrCustomizedFalse if customized pcs should be private to the user. (Needs change, foreign key to user needs to be added.)
    ordering = ['name']

