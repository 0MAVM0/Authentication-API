from .models import User, UserConfirmation, NEW, CODE_VERIFIED, DONE, PHOTO, VIA_EMAIL, VIA_NUMBER
from rest_framework.exceptions import ValidationError
from shared.utilities import validation_type
from rest_framework import serializers


class SignUpSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    def __init__(self, *args, **kwargs):
        super(SignUpSerializer, self).__init__(*args, **kwargs)
        self.fields['email_phone_number'] = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'auth_type', 'auth_status']
        extra_kwargs = {
            'auth_type' : { 'read_only' : True },
            'auth_status' : { 'read_only' : True, 'default' : NEW }
        }

    def validate(self, data):
        super(SignUpSerializer, self).validate(data)
        data = self.auth_validate(data)

        return data

    def create(self, validated_data):
        user = super(SignUpSerializer, self).create(validated_data)
        if user.auth_type == VIA_EMAIL:
            code = user.create_code(VIA_EMAIL)
        else:
            code = user.create_code(VIA_NUMBER)

        return user

    @staticmethod
    def auth_validate(data):
        print(data)
        user_input = str(data.get('email_phone_number')).lower()
        input_type = validation_type(user_input)

        if input_type == 'email':
            data = {
                'auth_type' : VIA_EMAIL,
                'email' : user_input
            }
        elif input_type == 'phone_number':
            data = {
                'auth_type' : VIA_NUMBER,
                'phone_number' : user_input
            }
        else:
            raise ValidationError('Something went wrong. Please check your input.')

        return data

    def to_representation(self, instance):
        data = super(SignUpSerializer, self).to_representation(instance)
        data.update(instance.token())

        return data
