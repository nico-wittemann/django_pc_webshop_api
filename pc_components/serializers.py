from rest_framework import serializers
from .models import Component, Pc

class ComponentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Component
        fields = '__all__'


class PcSerializer(serializers.ModelSerializer):
    components = serializers.PrimaryKeyRelatedField(queryset=Component.objects.all(), many=True)

    class Meta:
        model = Pc
        fields = '__all__'

