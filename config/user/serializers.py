from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from django.contrib.auth.password_validation import validate_password

from shared.utilities import check_email_or_phone
from user.models import User, VIA_PHONE, VIA_EMAIL, CODE_VERIFIED, DONE


class SignUpSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    def __init__(self, *args, **kwargs):
        super(SignUpSerializer, self).__init__(*args, **kwargs)
        self.fields['email_phone_number'] = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = (
            'id',
            'auth_type',
            'auth_status',
            'email_phone_number'
        )
        extra_kwargs = {
            'auth_type': { 'read_only' : True, 'required' : False},
            'auth_status': { 'read_only' : True, 'required' : False}
        }

    def create(self, validated_data):
        user = super(SignUpSerializer, self).create(validated_data)

        if user.auth_type == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            # send_email(user.email, code)
        elif user.auth_type == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            # send_email(user.phone_number, code)
            # send_phone_code(user.phone_number, code)

        user.save()
        print(f'User created: {user.email} with auth type: {user.auth_type} and code: {code}')

        return user

    def validate(self, data):
        super(SignUpSerializer, self).validate(data)
        data = self.auth_validate(data)

        return data

    @staticmethod
    def auth_validate(data):
        print(data)
        user_input = str(data.get('email_phone_number')).lower()
        input_type = check_email_or_phone(user_input)

        if input_type == 'email':
            data = {
                'email': user_input,
                'auth_type': VIA_EMAIL
            }
        elif input_type == 'phone':
            data = {
                'phone_number': user_input,
                'auth_type': VIA_PHONE
            }
        else:
            data = {
                'success': False,
                'message': 'You must send email or phone number'
            }

            raise ValidationError(data)

        return data

    def validate_email_phone_number(self, value):
        value = value.lower()

        if value and User.objects.filter(email=value).exists():
            data = {
                'success': False,
                'message': 'This Email Already Exists'
            }

            raise ValidationError(data)
        elif value and User.objects.filter(phone_number=value).exists():
            data = {
                'success': False,
                'message': 'This Phone Number Is Already Authenticated'
            }

            raise ValidationError(data)

        return value

    def to_representation(self, instance):
        data = super(SignUpSerializer, self).to_representation(instance)
        data.update(instance.token())

        return data


class ChangeUserSerializer(serializers.Serializer):
    first_name = serializers.CharField(write_only=True, required=True)
    last_name = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(write_only=True, required=True)
    password1 = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        password1 = data.get('password1', None)
        password2 = data.get('password2', None)

        if password1 != password2:
            raise ValidationError({
                'message' : 'Passwords Do Not Match'
            })
        if password1:
            validate_password(password2)
            validate_password(password1)

        return data
    
    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.username = validated_data.get('username', instance.username)

        if validated_data.get('password1'):
            instance.set_password(validated_data.get('password2'))

        if instance.auth_status == CODE_VERIFIED:
            instance.auth_status = DONE

        instance.save()

        return instance
