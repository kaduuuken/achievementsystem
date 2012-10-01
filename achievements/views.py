from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from models import Category, Achievement, Trophies
import settings

@login_required(login_url='/admin')
def Overview(request):
    category_list = Category.objects.filter(parent_category__isnull=True)
    all_achievements_count = float(0)
    all_achievements = Achievement.objects.all()
    for ach in all_achievements:
        all_achievements_count += 1
    achievements_count = 0
    achievements_accomplished = Achievement.objects.filter(users = request.user)
    for ach in achievements_accomplished:
        achievements_count += 1
    if all_achievements_count != 0:
        all_percent = int((achievements_count/all_achievements_count)*100)
        all_achievements_count = int(all_achievements_count)
    else:
        all_percent = 0
    trophies_list = [None]*(settings.SET_PARAMETER+1)
    trophies = Trophies.objects.all()
    for trophy in trophies:
        trophies_list[trophy.position] = trophy.achievement
    for cat in category_list:
            all_bar = Category.all_progressbar(cat, request.user)
            all_count = float(Category.count_all_achievements(cat))
            if all_count != 0:
                all_cat_percent = int((all_bar/all_count)*100)
            else:
                all_cat_percent = 0
    return render_to_response('achievements/index.html',
                              {'category_list': category_list, 'trophies_list': trophies_list, 'all_bar': all_bar, 
                               'all_percent': all_percent, 'all_cat_percent': all_cat_percent,#'all_child_bar': all_child_bar,
                               'achievements_count': achievements_count, 'all_achievements_count': all_achievements_count},
                              context_instance=RequestContext(request))

def TrophyView(request):
    category_list = Category.objects.filter(parent_category__isnull=True)
    return render_to_response('achievements/trophy.html', 
                              {'category_list': category_list}, 
                              context_instance=RequestContext(request))

def TrophyCategoryView(request, category_id):
    category_list = Category.objects.filter(parent_category__isnull=True)
    achievement_list = Achievement.objects.filter(category__parent_category__id = category_id)
    achievements_accomplished = Achievement.objects.filter(users = request.user)
    return render_to_response('achievements/trophy_category.html', 
                              {'category_list': category_list,'achievement_list': achievement_list, 
                               'achievements_accomplished': achievements_accomplished,}, 
                              context_instance=RequestContext(request))

def CategoryView(request, category_id):
    current_category = Category.objects.get(id = category_id)
    category_list = Category.objects.filter(parent_category__isnull=True)
    all_categories = Category.objects.all()
    children = Category.objects.filter(parent_category__id = category_id)
    achievement_list = Achievement.objects.filter(category__id = category_id)
    achievements_accomplished = Achievement.objects.filter(users = request.user)
    for cat in all_categories:
        if cat.id == int(category_id):
            progress = Category.progressbar(cat, request.user)
            pro_count = float(Category.count_achievements(cat))
            if pro_count != 0:
                pro_percent = int((progress/pro_count)*100)
            else:
                pro_percent = 0
            all_bar = Category.all_progressbar(cat, request.user)
            all_count = float(Category.count_all_achievements(cat))
            if all_count != 0:
                all_percent = int((all_bar/all_count)*100)
            else:
                all_percent = 0
    child_progress = []
    for child in children:
        child_progress.append(Category.progressbar(child, request.user))
    trophies_list = [None]*(settings.SET_PARAMETER+1)
    return render_to_response('achievements/category.html',
                              {'category_list': category_list,'all_categories': all_categories, 'trophies_list': trophies_list,
                               'progress': progress, 'child_progress': child_progress, 'all_bar': all_bar, 'all_percent': all_percent, 'pro_percent': pro_percent,
                               'achievement_list': achievement_list, 'achievements_accomplished': achievements_accomplished,'current_category': current_category, 'categoryID': category_id}, 
                              context_instance=RequestContext(request))