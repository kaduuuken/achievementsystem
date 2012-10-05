from models import Achievement, Category, Trophy, CollectionAchievement, Progress, ProgressAchievement, Task, TaskAchievement, TaskProgress
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db import models

class CategoryAdmin(admin.ModelAdmin):
    list_display=['name', 'parent_category']
    search_fields = ('name', 'parent_category')

class AchievementAdmin(admin.ModelAdmin):
    list_display=['name', 'description', 'category']
    search_fields = ('name', 'category')

class ProgressAdmin(admin.ModelAdmin):
    list_display=['progress_achievement', 'achieved_amount', 'user']

class ProgressAchievementAdmin(admin.ModelAdmin):
    list_display=['name', 'description', 'category']
    search_fields = ('name', 'category')
    formfield_overrides = {
        models.ManyToManyField: {'widget': FilteredSelectMultiple("user", False)}
    }

class TaskAchievementAdmin(admin.ModelAdmin):
    list_display=['name', 'description', 'category']
    search_fields = ('name', 'category')
    formfield_overrides = {
        models.ManyToManyField: {'widget': FilteredSelectMultiple("tasks", False)}
    }
    formfield_overrides = {
        models.ManyToManyField: {'widget': FilteredSelectMultiple("users", False)}
    }

class CollectionAchievementAdmin(admin.ModelAdmin):
    list_display=['name', 'description', 'category']
    search_fields = ('name', 'category')
    formfield_overrides = {
        models.ManyToManyField: {'widget': FilteredSelectMultiple("achievements", False)}
    }

class TaskAdmin(admin.ModelAdmin):
    list_display=['name', 'description']

class TaskProgressAdmin(admin.ModelAdmin):
    list_display=['task_achievement', 'user']
    formfield_overrides = {
        models.ManyToManyField: {'widget': FilteredSelectMultiple("tasks", False)}
    }

class TrophiesAdmin(admin.ModelAdmin):
    list_display=['achievement', 'position']

admin.site.register(Achievement, AchievementAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(ProgressAchievement, ProgressAchievementAdmin)
admin.site.register(Progress, ProgressAdmin)
admin.site.register(TaskAchievement, TaskAchievementAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(TaskProgress, TaskProgressAdmin)
admin.site.register(Trophy, TrophiesAdmin)
admin.site.register(CollectionAchievement, CollectionAchievementAdmin)