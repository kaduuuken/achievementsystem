from django.core.exceptions import ValidationError
import settings

# checks, if given value is higher than the set amounts of positions (set in achievements/settings.py)
def validate_max(value):
        if value >= settings.TROPHY_COUNT:
            raise ValidationError(u'There are only 0-%s positions' % (settings.TROPHY_COUNT-1))