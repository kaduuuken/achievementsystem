from django.core.exceptions import ValidationError
import settings

def validate_max(value):
        if value >= settings.TROPHY_COUNT:
            raise ValidationError(u'There are only 0-%s positions' % (settings.TROPHY_COUNT-1))