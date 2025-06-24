from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ComponentViewSet, PcViewSet

component_router = DefaultRouter()
component_router.register('components', ComponentViewSet)

pc_router = DefaultRouter()
pc_router.register('pcs', PcViewSet)


urlpatterns = [
    path('', include(component_router.urls)),
    path('', include(pc_router.urls)),
]
