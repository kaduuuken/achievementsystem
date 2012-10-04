from django.db import models
from django.contrib.auth.models import User
from filebrowser.fields import FileBrowseField
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MaxLengthValidator
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
