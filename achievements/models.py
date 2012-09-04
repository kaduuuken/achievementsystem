from django.db import models
from django.contrib.auth.models import User
from filebrowser.fields import FileBrowseField
from django.utils.translation import ugettext_lazy as _
import validate

class Category(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    parent_category = models.ForeignKey('self', blank=True, null=True, related_name="child_categories")
    
    def __unicode__(self):
        if (self.parent_category != None):
            return "%s -> %s" % (self.parent_category, self.name)
        else:
            return "%s" % (self.name)

class Achievement(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    description = models.TextField(_("Description"))
    points = models.IntegerField(blank=False, default=0)
    icon = FileBrowseField(_("Icon"), directory='icons/', format='image', max_length=255, blank=False)
    category = models.ForeignKey(Category)
    
    def __unicode__(self):
        return self.name

class UserAchievement(Achievement):
    users = models.ManyToManyField(User, related_name="achievements")

class ProgressAchievement(Achievement):
    required_amount = models.PositiveIntegerField()
    users = models.ManyToManyField(User, related_name="progress_achievements", through="Progress")

class Progress(models.Model):
    user = models.ForeignKey(User)
    progress_achievement = models.ForeignKey(ProgressAchievement)
    achieved_amount = models.PositiveIntegerField()

class Task(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    description = models.TextField(_("Description"))

class TaskAchievement(Achievement):
    tasks = models.ManyToManyField(Task)
    users = models.ManyToManyField(User, related_name="task_achievements", through="TaskProgress")

class TaskProgress(models.Model):
    user = models.ForeignKey(User)
    task_achievement = models.ForeignKey(TaskAchievement)
    completed_tasks = models.ManyToManyField(Task, limit_choices_to={})

class CollectionAchievement(Achievement):
    achievements = models.ManyToManyField(Achievement, related_name="collection_achievements")

class Trophies(models.Model):
    achievement = models.ForeignKey(Achievement, blank=True)
    user = models.ForeignKey(User)
    position = models.PositiveIntegerField(validators=[validate.validate_max()])

    class Meta:
        unique_together = ("user","position")