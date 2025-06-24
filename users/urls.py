from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import UserViewSet

users_router = DefaultRouter()
users_router.register('users', UserViewSet)


urlpatterns = [
    path('', include(users_router.urls)),
]

