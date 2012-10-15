from django.db import models
from django.db.models.signals import m2m_changed
from django.contrib.auth.models import User
from filebrowser.fields import FileBrowseField
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MaxLengthValidator
from django.template import Template, Context
from django.core.exceptions import ValidationError
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

class ProgressAchievement(Achievement):
    required_amount = models.PositiveIntegerField(blank=False, null=False)
    user = models.ManyToManyField(User, related_name="progress_achievements", through="Progress")

    def render(self, user):
        try:
            self.amount_progress.get(user=user)
        except:
            amount = 0
            percentage = 0
        else:
            achieved = self.amount_progress.get(user=user)
            amount = achieved.achieved_amount
            percentage = int(amount / float(self.required_amount) *100.0)
        #if amount == self.required_amount:
            #self.users.create(id=user.id)
        output = Template( "<div class='progress_bar'><div class='progress'><div class='bar' style='width: {{ percentage }}%'></div></div><div class='percent'><p style='margin-top: -40px'>{{ achieved_amount }} / {{ required_amount }}</p></div></div>")
        c = Context({"required_amount": self.required_amount, 'achieved_amount': amount, 'percentage': percentage})
        return output.render(c)

class Progress(models.Model):
    user = models.ForeignKey(User)
    progress_achievement = models.ForeignKey(ProgressAchievement, related_name="amount_progress")
    achieved_amount = models.PositiveIntegerField(blank=False)

    class Meta:
        unique_together = ("user", "progress_achievement")

    def __unicode__(self):
        return self.progress_achievement.name

    def clean(self):
        if self.achieved_amount > self.progress_achievement.required_amount:
            raise ValidationError('Achieved Amount may not be bigger than required amount')

class Task(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    description = models.TextField(_("Description"))

    def __unicode__(self):
        return self.name

class TaskAchievement(Achievement):
    tasks = models.ManyToManyField(Task)
    user = models.ManyToManyField(User, related_name="task_achievements", through="TaskProgress")

    def render(self, user):
        completed_task_list = []
        for task in self.task_progress.filter(user=user):
            for complete in task.completed_tasks.all():
                completed_task_list.append(complete)
        task_list = self.tasks.all()
        task_names = []
        for task in task_list:
            task_names.append(task)
        output = Template("{% for task in task_names %}<p style='float: left; padding: 5px;{% if task in completed_task_list %} color: #62C462{% endif %}'>{{ task.name }}</p>{% endfor %}")
        c = Context({"task_names": task_names, "completed_task_list": completed_task_list})
        return output.render(c)

class TaskProgress(models.Model):
    user = models.ForeignKey(User)
    task_achievement = models.ForeignKey(TaskAchievement, related_name="task_progress")
    completed_tasks = models.ManyToManyField(Task)

    def __unicode__(self):
        return self.task_achievement.name

class CollectionAchievement(Achievement):
    achievements = models.ManyToManyField(Achievement, related_name="collection_achievements")

    def render(self, user):
        print self.achievements.all()
        output = Template("{% for ach in achievements.all %}<p style='float: left; padding: 5px;{% if ach in achievements_accomplished %} color: #62C462{% endif %}'>{{ach.name}}</p>{% endfor %}")
        c = Context({"achievements": self.achievements, 'achievements_accomplished': Achievement.objects.filter(users = user)})
        return output.render(c)

class Trophy(models.Model):
    achievement = models.ForeignKey(Achievement, blank=False, related_name="trophy")
    user = models.ForeignKey(User)
    position = models.PositiveIntegerField(validators=[validate.validate_max], blank=False, null=False)

    class Meta:
        unique_together = (("user","position"),("user", "achievement"))

    def clean(self):
        try:
            self.achievement.users.get(id=self.user.id)
        except:
            raise ValidationError('This User has not earned this achievement yet')
        if self.user is None:
            raise ValidationError('Select an User')

    def __unicode__(self):
        return self.achievement.name