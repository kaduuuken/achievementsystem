from django import template

from achievements.models import Category, Trophy
from achievements import settings

register = template.Library()

# call single_category.html with the given parameters
@register.inclusion_tag('achievements/single_category.html')
def render_category(category, user):
    return {
        'category': category,
        'percentage': category.get_complete_percentage(user),
        'completed_achievements': category.count_all_complete_achievements(user)
    }

# call navigation.html with the given parameters
@register.inclusion_tag('achievements/navigation.html')
def render_navigation(current_category=None):
    return {
        'categories': Category.objects.filter(parent_category__isnull=True),
        'current_category': current_category,
    }

# call trophies.html with the given parameters
@register.inclusion_tag('achievements/trophies.html')
def render_trophies(user, takes_context=True):
    trophies = [None] * settings.TROPHY_COUNT
    # put trophy on the given position in an array
    for trophy in Trophy.objects.filter(user=user):
        trophies[trophy.position] = trophy
    return {'trophies': trophies}

# check type of achievement and return the accordingly render function
@register.simple_tag
def render_subachievement(user, achievement):
    if hasattr(achievement, 'progressachievement'):
        return achievement.progressachievement.render(user)
    if hasattr(achievement, 'taskachievement'):
        return achievement.taskachievement.render(user)
    if hasattr(achievement, 'collectionachievement'):
        return achievement.collectionachievement.render(user)
    else:
        return ""