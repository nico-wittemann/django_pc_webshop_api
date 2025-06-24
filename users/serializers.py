from rest_framework import serializers
from .models import User
from django.contrib.auth.hashers import make_password
from pc_components import serializers as pc_serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    pcs = pc_serializers.PcSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'created_at', 'password', 'pcs']

    def create(self, validated_data):
        """ Hash the password when instanciating a user password """
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """ Hash the password when updating a user password """
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().update(instance, validated_data)



