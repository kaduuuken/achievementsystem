from django import template

from achievements.models import Category, Trophy
from achievements import settings


register = template.Library()

@register.inclusion_tag('achievements/single_category.html')
def render_category(category, user):
    return {
        'category': category,
        'percentage': category.get_complete_percentage(user),
        'completed_achievements': category.count_all_complete_achievements(user)
    }

@register.inclusion_tag('achievements/navigation.html')
def render_navigation(current_category=None):
    return {
        'categories': Category.objects.filter(parent_category__isnull=True),
        'current_category': current_category,
    }

@register.inclusion_tag('achievements/trophies.html')
def render_trophies(user, takes_context=True):
    trophies = [None] * settings.TROPHY_COUNT
    for trophy in Trophy.objects.filter(user=user):
        trophies[trophy.position] = trophy
    return {'trophies': trophies}