from django.contrib.contenttypes import generic

from sharing.models import GroupShare, UserShare

class GroupShareInline(generic.GenericTabularInline):
    extra = 1
    model = GroupShare

class UserShareInline(generic.GenericTabularInline):
    extra = 1
    model = UserShare
