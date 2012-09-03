from django.db import models
from django.utils.translation import ugettext_lazy as _


class Category(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    parent_category = models.ForeignKey('self', blank=True, null=True, related_name="child_categories")

