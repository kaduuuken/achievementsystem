from models import Achievement, Category, CollectionAchievement, Progress, ProgressAchievement, Task, TaskAchievement, TaskProgress, Trophies, UserAchievement
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db import models

class CategoryAdmin(admin.ModelAdmin):
    list_display=['name', 'parent_category']
    search_fields = ('name', 'parent_category')

class AchievementAdmin(admin.ModelAdmin):
    list_display=['name', 'description', 'category']
    search_fields = ('name', 'category')

class ProgressAchievementAdmin(admin.ModelAdmin):
    list_display=['name', 'description', 'category']
    search_fields = ('name', 'category')
