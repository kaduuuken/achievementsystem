from django.http import HttpResponse
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from models import Category, Achievement, Trophy
import settings

# can only be shown, if user is logged in
@login_required(login_url='/admin')
# index.html / start page
def Overview(request):
    category_list = Category.objects.filter(parent_category__isnull=True)
    achievements_complete = Achievement.objects.filter(users = request.user).count()
    all_achievements = Achievement.objects.all().count()
    # calculates percentage of all accomplished achievements in the achievementsystem
    if all_achievements == 0:
        complete_percentage = 0
    else:
        complete_percentage = int(achievements_complete / float(all_achievements) * 100.0)
    return render_to_response('achievements/index.html',
                              {'category_list': category_list,
                               'complete_percentage': complete_percentage, 
                               'achievements_complete': achievements_complete,
                               'all_achievements': all_achievements},
                              context_instance=RequestContext(request))

# position_remote.html / content of trophy pop-up for selecting position
def PositionModalView(request, achievement_id):
    achievement = Achievement.objects.get(id=achievement_id)
    # array with length of set trophy positions
    positions = [None] * settings.TROPHY_COUNT
    return render_to_response('achievements/position_remote.html',
                              {'positions': positions,
                               'achievement': achievement},
                              context_instance=RequestContext(request))

# trophy_remote.html / content of trophy pop-up for selecting achievement
def TrophyModalView(request, trophy_pos):
    complete_achievements_list = Achievement.objects.filter(users=request.user)
    trophies = Trophy.objects.filter(user=request.user)
    trophy_achievements = []
    for trophy in trophies:
        trophy_achievements.append(trophy.achievement)
    return render_to_response('achievements/trophy_remote.html', 
                              {'trophy_pos': trophy_pos,
                               'complete_achievements_list': complete_achievements_list,
                               'trophies': trophy_achievements,
                               'user': request.user}, 
                              context_instance=RequestContext(request))

# overrides or creates a trophy on a specific position
def TrophyView(request, achievement_id, trophy_slot):
    achievement = Achievement.objects.get(id=achievement_id)
    try:
        current_trophy = Trophy.objects.get(user=request.user, position=trophy_slot)
    except:
        Trophy.objects.create(achievement=achievement, user=request.user, position=trophy_slot)
    else:
        Trophy.objects.filter(user=request.user, position=trophy_slot).update(achievement=achievement)
    current_trophy = Trophy.objects.get(user=request.user, position=trophy_slot)
    return redirect('/achievements/')

# category.html / passes all variables needed in category.html, single_category.html and achievement_list.html
def CategoryView(request, category_id):
    user = request.user
    category = Category.objects.get(id=category_id)
    category_list = Category.objects.filter(parent_category=category)
    achievements_complete = category.count_all_complete_achievements(request.user)
    all_achievements = category.count_all_achievements()
    # calculates percentage of all accomplished achievements in the category and its child categories
    if all_achievements == 0:
        complete_percentage = 0
    else:
        complete_percentage = int(achievements_complete / float(all_achievements) * 100.0)
    achievement_list = Achievement.objects.filter(category__id = category_id)
    achievements_accomplished = Achievement.objects.filter(users = request.user)
    trophies = Trophy.objects.filter(user=request.user)
    trophy_achievements = []
    for trophy in trophies:
        trophy_achievements.append(trophy.achievement)
    return render_to_response('achievements/category.html',
                              {'user': user,
                               'category': category,
                               'category_list': category_list,
                               'complete_percentage': complete_percentage, 
                               'achievements_complete': achievements_complete,
                               'all_achievements': all_achievements,
                               'achievement_list': achievement_list,
                               'achievements_accomplished': achievements_accomplished,
                               'trophies': trophy_achievements},
                              context_instance=RequestContext(request))