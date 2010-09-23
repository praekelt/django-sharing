import unittest

from django.contrib.auth.models import Group,  User
from django.contrib.contenttypes.models import ContentType
from django.db import models

from sharing.models import GroupShare, UserShare

class TestModel(models.Model):
    pass
models.register_models('sharing', TestModel)

class SharingBackendTestCase(unittest.TestCase):
    def test_has_perm(self):
        # Create test object, users and groups.
        obj = TestModel.objects.create(id=1)
        user = User.objects.create(username='user')
        group = Group.objects.create(name='group')
        group_user = User.objects.create(username='group_user')
        group_user.groups.add(group)
        group_user.save()
        
        # Return False if 'view' permission is not found for user.
        self.failIf(user.has_perm('view', obj))
        
        # Return False if 'change' permission is not found for user.
        self.failIf(user.has_perm('change', obj))
        
        # Return False if 'delete' permission is not found for user.
        self.failIf(user.has_perm('delete', obj))
        
        # Return False if 'view' permission is not found for group user.
        self.failIf(group_user.has_perm('view', obj))
        
        # Return False if 'change' permission is not found for group user.
        self.failIf(group_user.has_perm('change', obj))
        
        # Return False if 'delete' permission is not found for group user.
        self.failIf(group_user.has_perm('delete', obj))
       
        # Setup user share.
        UserShare.objects.create(
            user=user,
            can_view=True,
            can_change=True,
            can_delete=True,
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id,
        )
        
        # Return True if 'view' permission is found for user.
        self.failUnless(user.has_perm('view', obj))
        
        # Return True if 'change' permission is found for user.
        self.failUnless(user.has_perm('change', obj))
        
        # Return True if 'delete' permission is found for user.
        self.failUnless(user.has_perm('delete', obj))
       
       # Group share has not yet been setup, so should all still be unpermitted.
        # Return False if 'view' permission is not found for group user.
        self.failIf(group_user.has_perm('view', obj))
        
        # Return False if 'change' permission is not found for group user.
        self.failIf(group_user.has_perm('change', obj))
        
        # Return False if 'delete' permission is not found for group user.
        self.failIf(group_user.has_perm('delete', obj))
        
        # Setup group share.
        GroupShare.objects.create(
            group=group,
            can_view=True,
            can_change=True,
            can_delete=True,
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id,
        )
        
        # Return True if 'view' permission is found for group user.
        self.failUnless(group_user.has_perm('view', obj))
        
        # Return True if 'change' permission is found for group user.
        self.failUnless(group_user.has_perm('change', obj))
        
        # Return True if 'delete' permission is found for group user.
        self.failUnless(group_user.has_perm('delete', obj))

class ShareAdminTestCase(unittest.TestCase):
    def test_has_change_permission(self):
        from sharing.admin import ShareAdmin
        from django.contrib import admin
        ShareAdmin(TestModel, admin.site)

        ShareAdmin.has_change_permission
