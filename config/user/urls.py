from django.urls import path
from .views import *

urlpatterns = [
    path('registrate/', CreateAPIView.as_view())
]
