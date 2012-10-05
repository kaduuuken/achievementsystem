from django.db import models
from django.contrib.auth.models import User
from filebrowser.fields import FileBrowseField
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MaxLengthValidator
from django.template import Template, Context
import validate

class Category(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    parent_category = models.ForeignKey('self', blank=True, null=True, related_name="child_categories")
    
    def count_achievements(self):
        return self.achievements.all().count()
    
    def count_all_achievements(self):
        count = self.achievements.all().count()
        for cat in self.child_categories.all():
            count += cat.count_all_achievements()
        return count
    
    def count_complete_achievements(self, user):
        return self.achievements.filter(users=user).count()
    
    def count_all_complete_achievements(self, user):
        count = self.count_complete_achievements(user)
        for child in self.child_categories.all():
            count += child.count_all_complete_achievements(user)
        return count

    def get_complete_percentage(self, user):
        all = float(self.count_all_achievements())
        if all == 0:
            return 0
        return int(self.count_all_complete_achievements(user)/all*100)
    
    def __unicode__(self):
        if (self.parent_category != None):
            return "%s - %s" % (self.parent_category, self.name)
        else:
            return "%s" % (self.name)

class Achievement(models.Model):
    name = models.CharField(_("Name"), max_length=25)
    description = models.TextField(_("Description"), validators=[MaxLengthValidator(60)])
    points = models.IntegerField(blank=False, default=0)
    icon = FileBrowseField(_("Icon"), directory='icons/', format='image', max_length=255, blank=True)
    category = models.ForeignKey(Category, related_name="achievements")
    users = models.ManyToManyField(User, related_name="user_achievements", blank=True)

    def __unicode__(self):
        return self.name
    
    def get_subclass(self):
        if hasattr(self, 'progressachievement'):
            return self.progressachievement.render()
        if hasattr(self, 'taskachievement'):
            return self.taskachievement.render()
        if hasattr(self, 'collectionachievement'):
            return self.collectionachievement.render()

class ProgressAchievement(Achievement):
    required_amount = models.PositiveIntegerField()
    user = models.ManyToManyField(User, related_name="progress_achievements", through="Progress")
    
    def render(self):
        output = Template( "<p>{{ required_amount }}</p><p>{{ achieved_amount }}</p>")
        c = Context({"required_amount": self.required_amount})
        return output.render(c)

class Progress(models.Model):
    user = models.ForeignKey(User)
    progress_achievement = models.ForeignKey(ProgressAchievement, related_name="amount_progress")
    achieved_amount = models.PositiveIntegerField()

class Task(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    description = models.TextField(_("Description"))
    
    def __unicode__(self):
        return self.name

class TaskAchievement(Achievement):
    tasks = models.ManyToManyField(Task)
    user = models.ManyToManyField(User, related_name="task_achievements", through="TaskProgress")
    
    def render(self):
        completed_task_list = []
        for task in self.task_progress.filter(user=self.user.all()):
            for complete in task.completed_tasks.all():
                completed_task_list.append(complete)
        task_list = self.tasks.all()
        task_names = []
        for task in task_list:
            task_names.append(task)
        output = Template("{% for task in task_names %}<p style='float: left; padding: 5px;{% if not task in completed_task_list %} color: #990000{% endif %}'>{{ task.name }}</p>{% endfor %}")
        c = Context({"task_names": task_names, "completed_task_list": completed_task_list})
        return output.render(c)

class TaskProgress(models.Model):
    user = models.ForeignKey(User)
    task_achievement = models.ForeignKey(TaskAchievement, related_name="task_progress")
    completed_tasks = models.ManyToManyField(Task, limit_choices_to={})
    
    def __unicode__(self):
        return self.task_achievement.name

class CollectionAchievement(Achievement):
    achievements = models.ManyToManyField(Achievement, related_name="collection_achievements")
    
    def render(self):
        print self.achievements.all()
        output = Template("{% for ach in achievements %}<p>{{ach.name}}</p>{% endfor %}")
        c = Context({"achievements": self.achievements})
        return output.render(c)

class Trophy(models.Model):
    achievement = models.ForeignKey(Achievement, blank=True, related_name="trophy")
    user = models.ForeignKey(User)
    position = models.PositiveIntegerField(validators=[validate.validate_max])
    
    class Meta:
        unique_together = (("user","position"),("user", "achievement"))
    
    def clean(self):
        from django.core.exceptions import ValidationError
        try:
            self.achievement.users.get(id=self.user.id)
        except:
            raise ValidationError('This User has not earned this achievement yet')
        if self.user is None:
            raise ValidationError('Select an User')
    
    def __unicode__(self):
        return self.achievement.name
