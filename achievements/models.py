from django.db import models
from django.contrib.auth.models import User
from filebrowser.fields import FileBrowseField
from django.utils.translation import ugettext_lazy as _
import validate

class Category(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    parent_category = models.ForeignKey('self', blank=True, null=True, related_name="child_categories")
    
    def count_achievements(self):
        return self.achievements.all().count()
    
    def count_all_achievements(self):
        count = 0
        for cat in self.child_categories.all():
            count += cat.count_all_achievements()
        count += self.achievements.all().count()
        return count
    
    def progressbar(self, User):
        count = 0
        for ach in self.achievements.all():
            for user in ach.users.all():
                if user.username != User:
                    count += 1
        return count
    
    def all_progressbar(self, User):
        count = 0
        for child in self.child_categories.all():
            for ach in child.achievements.all():
                for user in ach.users.all():
                    if user.username != User:
                        count += 1   
        return count
    
    def __unicode__(self):
        if (self.parent_category != None):
            return "%s - %s" % (self.parent_category, self.name)
        else:
            return "%s" % (self.name)

class Achievement(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    description = models.TextField(_("Description"))
    points = models.IntegerField(blank=False, default=0)
    icon = FileBrowseField(_("Icon"), directory='icons/', format='image', max_length=255, blank=True)
    category = models.ForeignKey(Category, related_name="achievements")
    users = models.ManyToManyField(User, related_name="user_achievements", blank=True)
    
    def __unicode__(self):
        return self.name
    
    #def get_subclass(self):
        #if hasattr(self, 'progressachievement'):
            #return self.progressachievement
        #if hasattr(self, 'taskachievement'):
            #return self.taskachievement
        #if hasattr(self, 'collectionachievement'):
            #return self.collectionachievement
    
    def render(self):
        output = "<p><b>%s</b></p><p>%s</p>" % (self.name, self.description)
        return output

class Trophies(models.Model):
    achievement = models.ForeignKey(Achievement, blank=True)
    user = models.ForeignKey(User)
    position = models.PositiveIntegerField(validators=[validate.validate_max])
    
    class Meta:
        unique_together = ("user","position")
    
    def __unicode__(self):
        return self.achievement.name
