from rest_framework.exceptions import ValidationError
import re

EMAIL_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
PHONE_REGEX = r'^\\+?[1-9][0-9]{7,14}$'

def check_email_or_phone(user_input):
    if (re.fullmatch(EMAIL_REGEX, user_input)):
        data = 'email'
    elif (re.fullmatch(PHONE_REGEX, user_input)):
        data = 'phone_number'
    else:
        raise ValidationError('Input, you has given, is not valid.')

    return data
