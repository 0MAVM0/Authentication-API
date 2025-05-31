from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from django.utils.timezone import datetime

from .serializers import SignUpSerializer, ChangeUserSerializer
from .models import User, NEW, CODE_VERIFIED


class CreateUserAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    http_method_names = ['post']
    permission_classes = (AllowAny,)


class UserVerificationAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post']

    def post(self, *args, **kwargs):
        user = self.request.user
        code = self.request.data.get('code')

        self.verify(user, code)
        data = {
            'success' : True,
            'auth_status' : user.auth_status,
            'access' : user.token()['access'],
            'refresh_token' : user.token()['refresh_token'],
        }

        return Response(data)

    @staticmethod
    def verify(user, code):
        verifies = user.verify_codes.filter(code=code, expiration_time__gte=datetime.now(), is_confirmed=False)
        print(verifies)
        
        if not verifies.exists():
            data = {
                'success' : False,
                'message' : 'Your code is invalid or time is over'
            }

            raise ValidationError(data)
        verifies.update(is_confirmed=True)

        if user.auth_status == NEW:
            user.auth_status = CODE_VERIFIED
            user.save()

        return True


class ChangeUserAPIView(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['put', 'putch']

    def update(self, request, *args, **kwargs):
        super(ChangeUserAPIView, self).update(request, *args, **kwargs)
        data = {
            'success' : True,
            'message' : 'Authenticated Successfuly?',
            'auth_status' : self.request.user.auth_status
        }

        return Response(data)
