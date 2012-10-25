from models import Achievement, Category, Trophy, CollectionAchievement, Progress, ProgressAchievement, Task, TaskAchievement, TaskProgress
from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db import models

class CategoryAdmin(admin.ModelAdmin):
    list_display=['name', 'parent_category']
    search_fields = ('name', 'parent_category')

class AchievementAdminForm(forms.ModelForm):
    class Meta:
        model = Achievement

    def clean(self):
        users = self.cleaned_data.get('users')
        progress = Progress.objects.filter(progress_achievement__id = self.instance.id)
        taskprogress = TaskProgress.objects.filter(task_achievement__id = self.instance.id)
        if self.instance.id:
            if users:
                try:
                    progressachievement = ProgressAchievement.objects.get(id = self.instance.id)
                except:
                    try:
                        taskachievement = TaskAchievement.objects.get(id = self.instance.id)
                    except:
                        try:
                            collectionachievement = CollectionAchievement.objects.get(id = self.instance.id)
                        except:
                            return self.cleaned_data
                        else:
                            for achievement in collectionachievement.achievements.all():
                                for user in users:
                                    if not user in achievement.users.all():
                                        raise ValidationError('This User has not earned this achievement yet')
                            return self.cleaned_data
                    else:
                        if not taskprogress:
                            raise ValidationError('This User has not earned this achievement yet')
                        else:
                            for pro in taskprogress:
                                if pro.user in users:
                                    if not pro.completed_tasks.count() == taskachievement.tasks.count():
                                        raise ValidationError('This User has not earned this achievement yet')
                                    else:
                                        if not users.count() == 1:
                                            raise ValidationError('This User has not earned this achievement yet')
                                        else:
                                            return self.cleaned_data
                                else:
                                    if taskprogress.count() == 1:
                                        raise ValidationError('This User has not earned this achievement yet')
                            raise ValidationError('This User has not earned this achievement yet')
                else:
                    if not progress:
                        raise ValidationError('This User has not earned this achievement yet')
                    else:
                        for pro in progress:
                            if pro.user in users:
                                if not pro.achieved_amount == progressachievement.required_amount:
                                    raise ValidationError('This User has not earned this achievement yet')
                                else:
                                    if not users.count() == 1:
                                        raise ValidationError('This User has not earned this achievement yet')
                                    else:
                                        return self.cleaned_data
                            else:
                                if progress.count() == 1:
                                    raise ValidationError('This User has not earned this achievement yet')
                        raise ValidationError('This User has not earned this achievement yet')
            else:
                return self.cleaned_data
        elif users:
            raise ValidationError('You can not add user for this achievement yet')
        else:
            return self.cleaned_data

class AchievementAdmin(admin.ModelAdmin):
    form = AchievementAdminForm
    list_display=['name', 'description', 'category']
    search_fields = ('name', 'category')
    formfield_overrides = {
        models.ManyToManyField: {'widget': FilteredSelectMultiple("user", False)}
    }

class ProgressAdmin(admin.ModelAdmin):
    list_display=['progress_achievement', 'achieved_amount', 'user']

class ProgressAchievementAdminForm(forms.ModelForm):
    class Meta:
        model = ProgressAchievement
    
    def clean(self):
        users = self.cleaned_data.get('users')
        required_amount = self.cleaned_data.get('required_amount')
        progress = Progress.objects.filter(progress_achievement__id = self.instance.id)
        if self.instance.id:
            if users:
                if not progress:
                    raise ValidationError('This User has not earned this achievement yet')
                else:
                    for pro in progress:
                        if pro.user in users:
                            if not pro.achieved_amount == required_amount:
                                raise ValidationError('This User has not earned this achievement yet')
                            else:
                                if not users.count() == 1:
                                    raise ValidationError('This User has not earned this achievement yet')
                                else:
                                    return self.cleaned_data
                        else:
                            if progress.count() == 1:
                                raise ValidationError('This User has not earned this achievement yet')
                    raise ValidationError('This User has not earned this achievement yet')
            else:
                return self.cleaned_data
        elif users:
            raise ValidationError('You can not add user for this achievement yet')
        else:
            return self.cleaned_data

class ProgressAchievementAdmin(admin.ModelAdmin):
    form = ProgressAchievementAdminForm
    list_display=['name', 'description', 'category']
    search_fields = ('name', 'category')
    formfield_overrides = {
        models.ManyToManyField: {'widget': FilteredSelectMultiple("user", False)}
    }

class TaskAchievementAdminForm(forms.ModelForm):
    class Meta:
        model = TaskAchievement
    
    def clean(self):
        users = self.cleaned_data.get('users')
        tasks = self.cleaned_data.get('tasks')
        progress = TaskProgress.objects.filter(task_achievement__id = self.instance.id)
        if self.instance.id:
            if users:
                if not progress:
                    raise ValidationError('This User has not earned this achievement yet')
                else:
                    for pro in progress:
                        if pro.user in users:
                            if not pro.completed_tasks.count() == tasks.count():
                                raise ValidationError('This User has not earned this achievement yet')
                            else:
                                if not users.count() == 1:
                                    raise ValidationError('This User has not earned this achievement yet')
                                else:
                                    return self.cleaned_data
                        else:
                            if progress.count() == 1:
                                raise ValidationError('This User has not earned this achievement yet')
                    raise ValidationError('This User has not earned this achievement yet')
            else:
                return self.cleaned_data
        elif users:
            raise ValidationError('You can not add user for this achievement yet')
        else:
            return self.cleaned_data

class TaskAchievementAdmin(admin.ModelAdmin):
    form = TaskAchievementAdminForm
    list_display=['name', 'description', 'category']
    search_fields = ('name', 'category')
    formfield_overrides = {
        models.ManyToManyField: {'widget': FilteredSelectMultiple("tasks", False)}
    }
    formfield_overrides = {
        models.ManyToManyField: {'widget': FilteredSelectMultiple("users", False)}
    }

class CollectionAchievementAdminForm(forms.ModelForm):
    class Meta:
        model = CollectionAchievement
    
    def clean(self):
        users = self.cleaned_data.get('users')
        achievements = self.cleaned_data.get('achievements')
        if users:
            for achievement in achievements:
                for user in users:
                    if not user in achievement.users.all():
                        raise ValidationError('This User has not earned this achievement yet')
            return self.cleaned_data
        else:
            return self.cleaned_data

class CollectionAchievementAdmin(admin.ModelAdmin):
    form = CollectionAchievementAdminForm
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