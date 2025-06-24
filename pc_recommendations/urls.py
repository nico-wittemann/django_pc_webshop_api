from django.urls import path
from .views import PCRecommendationView

urlpatterns = [
    path('recommend/', PCRecommendationView.as_view(), name='pc-recommendation'),
] 