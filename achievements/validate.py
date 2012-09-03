from django.core.exceptions import ValidationError
import settings

def validate_max(value):
        if value > settings.SET_PARAMETER:
            raise ValidationError(u'There are only %s positions' % settings.SET_PARAMETER)