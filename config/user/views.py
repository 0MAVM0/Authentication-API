from rest_framework.generics import CreateAPIView
from .sertializers import SignUpSerializer
from .models import User


class CreateUserAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    http_method_names = ['post']
