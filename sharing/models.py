from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models

class Share(models.Model):
    """
    Abstract share model storing a generic object relation and permissions.
    """
    can_view = models.BooleanField()
    can_change = models.BooleanField()
    can_delete = models.BooleanField()

    content_type = models.ForeignKey(ContentType)
    object_id = models.IntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        abstract = True

class GroupShare(Share):
    """
    Group share model associating object permissions with a group.
    """
    group = models.ForeignKey('auth.Group')
    
    def __unicode__(self):
        return '%s share' % self.group


class UserShare(Share):
    """
    User share model associating object permissions with a user.
    """
    user = models.ForeignKey(
        'auth.User',
        limit_choices_to={'is_staff': True,},
    )
    
    def __unicode__(self):
        return '%s share' % self.user
