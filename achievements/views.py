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
    print trophies_list
    return render_to_response('achievements/index.html',{'category_list': category_list, 'trophies_list': trophies_list})

def CategoryView(request, category_id):
    category_list = Category.objects.filter(parent_category__isnull=True)
    all_categories = Category.objects.all()
    achievement_list = Achievement.objects.filter(category__id = category_id)
    
    return render_to_response('achievements/category.html',
                              {'category_list': category_list,'all_categories': all_categories, 'achievement_list': achievement_list, 'categoryID': category_id},
                              context_instance=RequestContext(request))