from django.db import models
from django.contrib.auth.models import User

class AuditedModel(models.Model):
    created_at = models.DateTimeField(null=False, blank=False, auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='created_%(class)s_set', null=False, blank=True)
    modified_at = models.DateTimeField(null=False, blank=False, auto_now=True)
    modified_by = models.ForeignKey(User, related_name='modified_%(class)s_set', null=False, blank=True)

    class Meta:
        abstract = True

class LooselyAuditedModel(models.Model):
    created_at = models.DateTimeField(null=False, blank=False, auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='created_%(class)s_set', null=True, blank=True)
    modified_at = models.DateTimeField(null=False, blank=False, auto_now=True)
    modified_by = models.ForeignKey(User, related_name='modified_%(class)s_set', null=True, blank=True)

    class Meta:
        abstract = True
