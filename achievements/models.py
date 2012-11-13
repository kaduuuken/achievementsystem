from django.db import models
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
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

    # count all achievements according to the selected category
    def count_achievements(self):
        return self.achievements.all().count()

    # count all achievements according to the selected category and its child categories
    def count_all_achievements(self):
        count = self.achievements.all().count()
        for cat in self.child_categories.all():
            count += cat.count_all_achievements()
        return count

    # count all achievement according to the selected category, which have been accomplished
    def count_complete_achievements(self, user):
        return self.achievements.filter(users=user).count()

    # count all achievement according to the selected category and its child categories, which have been accomplished
    def count_all_complete_achievements(self, user):
        count = self.count_complete_achievements(user)
        for child in self.child_categories.all():
            count += child.count_all_complete_achievements(user)
        return count

    # percentage of accomplished achievements for the selected category and its child categories
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

    # returns progress bar and its content as template
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

    # value of achieved amount may not be bigger than the required amount
    def clean(self):
        if self.achieved_amount > self.progress_achievement.required_amount:
            raise ValidationError('Achieved Amount may not be bigger than required amount')

# if achieved amount of progress table is the same as the required amount of the progress achievement table
# the according user of the progress will be added to the progress achievement
@receiver(post_save, sender=Progress)
def set_progress_user(sender, instance, created, **kwargs):
    if instance.achieved_amount == instance.progress_achievement.required_amount:
        instance.progress_achievement.users.add(instance.user)
    elif instance.user in instance.progress_achievement.users.all():
            instance.progress_achievement.users.remove(instance.user)

class Task(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    description = models.TextField(_("Description"))

    def __unicode__(self):
        return self.name

class TaskAchievement(Achievement):
    tasks = models.ManyToManyField(Task)
    user = models.ManyToManyField(User, related_name="task_achievements", through="TaskProgress")

    # returns required tasks as template
    # task is green if accomplished, grey if not
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

# if user has accomplished all required tasks, he will be added to the according task achievement
@receiver(m2m_changed, sender=TaskProgress.completed_tasks.through)
def set_task_user(sender, instance, action, reverse, model, pk_set, **kwargs):
    if instance.completed_tasks.count() == instance.task_achievement.tasks.count():
        instance.task_achievement.users.add(instance.user)
    elif instance.user in instance.task_achievement.users.all():
            instance.task_achievement.users.remove(instance.user)

class CollectionAchievement(Achievement):
    achievements = models.ManyToManyField(Achievement, related_name="collection_achievements")

    # returns required achievements as template
    # achievement is green if accomplished, grey if not
    def render(self, user):
        print self.achievements.all()
        output = Template("{% for ach in achievements.all %}<p style='float: left; padding: 5px;{% if ach in achievements_accomplished %} color: #62C462{% endif %}'>{{ach.name}}</p>{% endfor %}")
        c = Context({"achievements": self.achievements, 'achievements_accomplished': Achievement.objects.filter(users = user)})
        return output.render(c)

# if user has accomplished all required achievements, he will be added to the according collection achievement
@receiver(m2m_changed, sender=Achievement.users.through)
def set_collection_user(sender, instance, action, reverse, model, pk_set,  **kwargs):
    collectionachievement = []
    # is achievement an required achievement of an collection achievement
    if instance.collection_achievements.all():
        for ach in instance.collection_achievements.all():
            # add all collection achievements, in which the selected achievement is required, to an array
            collectionachievement.append(CollectionAchievement.objects.get(id = ach.id))
        # if user has no longer accomplished the achievement, he will be removed from the according collection achievement
        if action == "post_clear":
            if not instance.users.all():
                for collection in collectionachievement:
                    for collect_user in collection.users.all():
                        if not collect_user in instance.users.all():
                            collection.users.remove(collect_user)
        # if a new user is added to the selected achievement, all other achievements according to the same collection achievement
        # will be checked on the same user
        # if the user has accomplished all required achievement, he will be added to the collection achievement
        elif action == "post_add":
            for collection in collectionachievement:
                not_earned_users = []
                earned_achievements = []
                earned_achievements.append(instance)
                for achievement in collection.achievements.all():
                    for user in instance.users.all():                        
                        if not achievement.id == instance.id:
                            # check, if user has accomplished other required achievement of the collection achievement
                            if user in achievement.users.all():
                                if not achievement in earned_achievements:
                                    # add other required achievement to an array
                                    earned_achievements.append(achievement)
                            elif not user in not_earned_users:
                                # add user to an array
                                not_earned_users.append(user)
                # check, if amount of earned achievements is the same as the amount of required achievements in the collection achievement
                if len(earned_achievements) == collection.achievements.count():
                    if collection.users.all():
                        for collect_user in collection.users.all():
                            if collect_user in instance.users.all():
                                for user in instance.users.all():
                                    if not user in not_earned_users:
                                        collection.users.add(user)
                            else:
                                collection.users.remove(collect_user)
                    else:
                        for user in instance.users.all():
                            # check, if user is not in array, which contains the users, which have not earned all required achievements
                            if not user in not_earned_users:
                                collection.users.add(user)

class Trophy(models.Model):
    achievement = models.ForeignKey(Achievement, blank=False, related_name="trophy")
    user = models.ForeignKey(User)
    # function validate_max in validate.py checks, if given value is higher than the set amounts of positions (set in achievements/settings.py)
    position = models.PositiveIntegerField(validators=[validate.validate_max], blank=False, null=False)

    class Meta:
        unique_together = (("user","position"),("user", "achievement"))

    # check, if selected achievement has already been accomplished
    # check, if user has been selected
    def clean(self):
        try:
            self.achievement.users.get(id=self.user.id)
        except:
            raise ValidationError('This User has not earned this achievement yet')
        if self.user is None:
            raise ValidationError('Select an User')

    def __unicode__(self):
        return self.achievement.name