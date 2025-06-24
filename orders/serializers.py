from rest_framework import serializers
from .models import Order, Order_Item
from pc_components.models import Pc, Component


class OrderSerializer(serializers.ModelSerializer):
    user_id = serializers.ReadOnlyField(source='user.id')
    class Meta:
        model = Order
        exclude = ['user']


class Order_ItemSerializer(serializers.ModelSerializer):
    pc_id = serializers.PrimaryKeyRelatedField(
        queryset=Pc.objects.all(), source="pc", write_only=True, required=False
    )
    component_id = serializers.PrimaryKeyRelatedField(
        queryset=Component.objects.all(), source="component", write_only=True, required=False
    )

    class Meta:
        model = Order_Item
        fields = '__all__'

    def validate_component(self, value):
        if self.initial_data.get('order_type') == 'pc' and self.initial_data.get('component') is None:
            raise serializers.ValidationError("Component must be specified for 'pc' type order.")
        return value

    def validate_pc(self, value):
        if self.initial_data.get('order_type') == 'component' and self.initial_data.get('pc') is None:
            raise serializers.ValidationError("Pc must be specified for 'component' type order.")
        return value