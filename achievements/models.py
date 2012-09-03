from django.db import models
from django.contrib.auth.models import User
from filebrowser.fields import FileBrowseField
from django.utils.translation import ugettext_lazy as _


class Category(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    parent_category = models.ForeignKey('self', blank=True, null=True, related_name="child_categories")

class Achievement(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    description = models.TextField(_("Description"))
    points = models.IntegerField(blank=False, default=0)
    icon = FileBrowseField(_("Icon"), directory='icons/', format='image', max_length=255, blank=False)
    category = models.ForeignKey(Category)

class UserAchievement(Achievement):
    users = models.ManyToManyField(User, related_name="achievements")

class ProgressAchievement(Achievement):
    required_amount = models.PositiveIntegerField()
    users = models.ManyToManyField(User, related_name="progress_achievements", through="Progress")

class Progress(models.Model):
    user = models.ForeignKey(User)
    progress_achievement = models.ForeignKey(ProgressAchievement)
    achieved_amount = models.PositiveIntegerField()