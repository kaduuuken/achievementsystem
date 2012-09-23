from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.views.generic import ListView
from models import Category, Achievement, Trophies
import settings

def Overview(request):
    category_list = Category.objects.filter(parent_category__isnull=True)
    trophies_list = [None]*(settings.SET_PARAMETER+1)
    trophies = Trophies.objects.all()
    for trophy in trophies:
        trophies_list[trophy.position] = trophy.achievement
    return render_to_response('achievements/index.html',
                              {'category_list': category_list, 'trophies_list': trophies_list},
                              context_instance=RequestContext(request))

def CategoryView(request, category_id):
    category_list = Category.objects.filter(parent_category__isnull=True)
    all_categories = Category.objects.all()
    children = Category.objects.filter(parent_category__id = category_id)
    achievement_list = Achievement.objects.filter(category__id = category_id)
    achievements_accomplished = Achievement.objects.filter(users = request.user)
    for cat in all_categories:
        if cat.id == int(category_id):
            progress = Category.progressbar(cat, request.user)
            all_bar = Category.all_progressbar(cat, request.user)
    child_progress = []
    for child in children:
        child_progress.append(Category.progressbar(child, request.user))
    return render_to_response('achievements/category.html',
                              {'category_list': category_list,'all_categories': all_categories, 
                               'progress': progress, 'child_progress': child_progress, 'all_bar': all_bar,
                               'achievement_list': achievement_list, 'achievements_accomplished': achievements_accomplished, 'categoryID': category_id}, 
                              context_instance=RequestContext(request))