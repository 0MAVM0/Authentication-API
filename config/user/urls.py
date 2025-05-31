from django.urls import path
from .views import *

urlpatterns = [
    path('registrate/', CreateAPIView.as_view()),
    path('verificate/', UserVerificationAPIView.as_view()),
    path('update/', ChangeUserAPIView.as_view()),
]
