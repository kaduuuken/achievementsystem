from django.conf import settings

# Defines the number of available trophy slots
TROPHY_COUNT = getattr(settings, 'ACHIEVEMENT_TROPHY_COUNT', 5)