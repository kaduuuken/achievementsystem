from models import Achievement, Category, Trophy, CollectionAchievement, Progress, ProgressAchievement, Task, TaskAchievement, TaskProgress
from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db import models

# set display and search field for category table
class CategoryAdmin(admin.ModelAdmin):
    list_display=['name', 'parent_category']
    search_fields = ('name', 'parent_category')

# ModelForm for validating, if an user has reached the achievement
class AchievementAdminForm(forms.ModelForm):
    class Meta:
        model = Achievement

    def clean(self):
        users = self.cleaned_data.get('users')
        progress = Progress.objects.filter(progress_achievement__id = self.instance.id)
        taskprogress = TaskProgress.objects.filter(task_achievement__id = self.instance.id)
        task_accomplished_user = []
        progress_accomplished_user = []
        # check, if achievement already exists
        if self.instance.id:
            # check, if achievement has any users
            if users:
                # check, if achievement is one of the sub types
                try:
                    progressachievement = ProgressAchievement.objects.get(id = self.instance.id)
                except:
                    try:
                        taskachievement = TaskAchievement.objects.get(id = self.instance.id)
                    except:
                        try:
                            collectionachievement = CollectionAchievement.objects.get(id = self.instance.id)
                        except:
                            # if achievement is not one of them, it can be saved, because there are no requirements, which have to be checked
                            return self.cleaned_data
                        else:
                            # check, if user in CollectionAchievement has accomplished all achievements, which are required in the CollectionAchievement
                            for achievement in collectionachievement.achievements.all():
                                for user in users:
                                    if not user in achievement.users.all():
                                        raise ValidationError('This User has not earned this achievement yet')
                            return self.cleaned_data
                    else:
                        # check, if there is any TaskProgress for this TaskAchievement
                        if not taskprogress:
                            raise ValidationError('This User has not earned this achievement yet')
                        else:
                            for pro in taskprogress:
                                if pro.user in users:
                                    # check, if user has accomplished all required tasks
                                    if not pro.completed_tasks.count() == taskachievement.tasks.count():
                                        raise ValidationError('This User has not earned this achievement yet')
                                    else:
                                        # check, if users contains only 1 entry
                                        # if not, the user of the accomplished achievement will be saved in an array
                                        if not users.count() == 1:
                                            task_accomplished_user.append(pro.user)
                                        else:
                                            return self.cleaned_data
                                else:
                                    # check, if TaskProgress contains only 1 entry
                                    if taskprogress.count() == 1:
                                        raise ValidationError('This User has not earned this achievement yet')
                            # check, if amount of entries in array, which contains the user of the accomplished achievements, 
                            # is the same as the amount of entries of users list
                            if not len(task_accomplished_user) == users.count():
                                raise ValidationError('This User has not earned this achievement yet')
                            else:
                                return self.cleaned_data
                else:
                    # check, if there is any Progress for this ProgressAchievement
                    if not progress:
                        raise ValidationError('This User has not earned this achievement yet')
                    else:
                        for pro in progress:
                            if pro.user in users:
                                # check, if user has accomplished the required amount
                                if not pro.achieved_amount == progressachievement.required_amount:
                                    raise ValidationError('This User has not earned this achievement yet')
                                else:
                                    # check, if users contains only 1 entry
                                    # if not, the user of the accomplished achievement will be saved in an array
                                    if not users.count() == 1:
                                        progress_accomplished_user.append(pro.user)
                                    else:
                                        return self.cleaned_data
                            else:
                                # check, if TaskProgress contains only 1 entry
                                if progress.count() == 1:
                                    raise ValidationError('This User has not earned this achievement yet')
                        # check, if amount of entries in array, which contains the user of the accomplished achievements, 
                        # is the same as the amount of entries of users list
                        if not len(progress_accomplished_user) == users.count():
                            raise ValidationError('This User has not earned this achievement yet')
                        else:
                            return self.cleaned_data
            else:
                return self.cleaned_data
        else:
            return self.cleaned_data

# set display and search field for achievement table
# include AchievementAdminForm
# set ManyToManyField users to FilteredSelectMultiple
class AchievementAdmin(admin.ModelAdmin):
    form = AchievementAdminForm
    list_display=['name', 'description', 'category']
    search_fields = ('name', 'category')
    formfield_overrides = {
        models.ManyToManyField: {'widget': FilteredSelectMultiple("user", False)}
    }

# set display field for progress table
class ProgressAdmin(admin.ModelAdmin):
    list_display=['progress_achievement', 'achieved_amount', 'user']

# ModelForm for validating, if an user has reached the ProgressAchievement
class ProgressAchievementAdminForm(forms.ModelForm):
    class Meta:
        model = ProgressAchievement
    
    def clean(self):
        users = self.cleaned_data.get('users')
        required_amount = self.cleaned_data.get('required_amount')
        progress = Progress.objects.filter(progress_achievement__id = self.instance.id)
        accomplished_user = []
        if self.instance.id:
            if users:
                # check, if there is any Progress for this ProgressAchievement
                if not progress:
                    raise ValidationError('This User has not earned this achievement yet')
                else:
                    for pro in progress:
                        if pro.user in users:
                            # check, if user has accomplished the required amount
                            if not pro.achieved_amount == required_amount:
                                raise ValidationError('This User has not earned this achievement yet')
                            else:
                                # check, if users contains only 1 entry
                                # if not, the user of the accomplished achievement will be saved in an array
                                if not users.count() == 1:
                                    accomplished_user.append(pro.user)
                                else:
                                    return self.cleaned_data
                        else:
                            # check, if TaskProgress contains only 1 entry
                            if progress.count() == 1:
                                raise ValidationError('This User has not earned this achievement yet')
                    # check, if amount of entries in array, which contains the user of the accomplished achievements, 
                    # is the same as the amount of entries of users list
                    if not len(accomplished_user) == users.count():
                        raise ValidationError('This User has not earned this achievement yet')
                    else:
                        return self.cleaned_data
            else:
                return self.cleaned_data
        # if ProgressAchievement is new, it cannot be accomplished yet
        elif users:
            raise ValidationError('You can not add user for this achievement yet')
        else:
            return self.cleaned_data

# set display and search field for ProgressAchievement table
# include ProgressAchievementAdminForm
# set ManyToManyField users to FilteredSelectMultiple
class ProgressAchievementAdmin(admin.ModelAdmin):
    form = ProgressAchievementAdminForm
    list_display=['name', 'description', 'category']
    search_fields = ('name', 'category')
    formfield_overrides = {
        models.ManyToManyField: {'widget': FilteredSelectMultiple("user", False)}
    }

# ModelForm for validating, if an user has reached the TaskAchievement
class TaskAchievementAdminForm(forms.ModelForm):
    class Meta:
        model = TaskAchievement
    
    def clean(self):
        users = self.cleaned_data.get('users')
        tasks = self.cleaned_data.get('tasks')
        progress = TaskProgress.objects.filter(task_achievement__id = self.instance.id)
        accomplished_user = []
        if self.instance.id:
            if users:
                # check, if there is any TaskProgress for this TaskAchievement
                if not progress:
                    raise ValidationError('This User has not earned this achievement yet')
                else:
                    for pro in progress:
                        if pro.user in users:
                            # check, if user has accomplished all required tasks
                            if not pro.completed_tasks.count() == tasks.count():
                                raise ValidationError('This User has not earned this achievement yet')
                            else:
                                # check, if users contains only 1 entry
                                # if not, the user of the accomplished achievement will be saved in an array
                                if not users.count() == 1:
                                    accomplished_user.append(pro.user)
                                else:
                                    return self.cleaned_data
                        else:
                            # check, if TaskProgress contains only 1 entry
                            if progress.count() == 1:
                                raise ValidationError('This User has not earned this achievement yet')
                    # check, if amount of entries in array, which contains the user of the accomplished achievements, 
                    # is the same as the amount of entries of users list
                    if not len(accomplished_user) == users.count():
                        raise ValidationError('This User has not earned this achievement yet')
                    else:
                        return self.cleaned_data
            else:
                return self.cleaned_data
        # if TaskAchievement is new, it cannot be accomplished yet
        elif users:
            raise ValidationError('You can not add user for this achievement yet')
        else:
            return self.cleaned_data

# set display and search field for TaskAchievement table
# include TaskAchievementAdminForm
# set ManyToManyField tasks to FilteredSelectMultiple
# set ManyToManyField users to FilteredSelectMultiple
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

# ModelForm for validating, if an user has reached the CollectionAchievement
class CollectionAchievementAdminForm(forms.ModelForm):
    class Meta:
        model = CollectionAchievement
    
    def clean(self):
        users = self.cleaned_data.get('users')
        achievements = self.cleaned_data.get('achievements')
        if users:
            # check, if user in CollectionAchievement has accomplished all achievements, which are required in the CollectionAchievement
            for achievement in achievements:
                for user in users:
                    if not user in achievement.users.all():
                        raise ValidationError('This User has not earned this achievement yet')
            return self.cleaned_data
        else:
            return self.cleaned_data

# set display and search field for CollectionAchievement table
# include CollectionAchievementAdminForm
# set ManyToManyField achievements to FilteredSelectMultiple
class CollectionAchievementAdmin(admin.ModelAdmin):
    form = CollectionAchievementAdminForm
    list_display=['name', 'description', 'category']
    search_fields = ('name', 'category')
    formfield_overrides = {
        models.ManyToManyField: {'widget': FilteredSelectMultiple("achievements", False)}
    }

# set display field for Task table
class TaskAdmin(admin.ModelAdmin):
    list_display=['name', 'description']

# set display field for TaskProgress table
# # set ManyToManyField tasks to FilteredSelectMultiple
class TaskProgressAdmin(admin.ModelAdmin):
    list_display=['task_achievement', 'user']
    formfield_overrides = {
        models.ManyToManyField: {'widget': FilteredSelectMultiple("tasks", False)}
    }

# set display field for Trophy table
class TrophyAdmin(admin.ModelAdmin):
    list_display=['achievement', 'position']

admin.site.register(Achievement, AchievementAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(ProgressAchievement, ProgressAchievementAdmin)
admin.site.register(Progress, ProgressAdmin)
admin.site.register(TaskAchievement, TaskAchievementAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(TaskProgress, TaskProgressAdmin)
admin.site.register(Trophy, TrophyAdmin)
admin.site.register(CollectionAchievement, CollectionAchievementAdmin)