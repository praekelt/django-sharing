import unittest

from django.contrib import admin
from django.contrib.auth.models import Group,  User
from django.contrib.contenttypes.models import ContentType
from django.db import models

from sharing import utils
from sharing.admin import ShareAdminMixin
from sharing.models import GroupShare, UserShare
from snippetscream import RequestFactory

class TestModel(models.Model):
    pass
models.register_models('sharing', TestModel)

class TestModelAdmin(ShareAdminMixin, admin.ModelAdmin):
    pass
admin.site.register(TestModel, TestModelAdmin)

class ShareBackendTestCase(unittest.TestCase):
    def setUp(self):
        # Create test object, users and groups.
        self.obj = TestModel.objects.create(id=1)
        self.user = User.objects.create(username='user')
        self.group = Group.objects.create(name='group')
        self.group_user = User.objects.create(username='group_user')
        self.group_user.groups.add(self.group)
        self.group_user.save()
    
    def tearDown(self):
        # Delete created objects.
        self.obj.delete()
        self.user.delete()
        self.group.delete()
        self.group_user.delete()

    def test_has_perm(self):
        # Return False if 'view' permission is not found for user.
        self.failIf(self.user.has_perm('view', self.obj))
        
        # Return False if 'change' permission is not found for user.
        self.failIf(self.user.has_perm('change', self.obj))
        
        # Return False if 'delete' permission is not found for user.
        self.failIf(self.user.has_perm('delete', self.obj))
        
        # Return False if 'view' permission is not found for group user.
        self.failIf(self.group_user.has_perm('view', self.obj))
        
        # Return False if 'change' permission is not found for group user.
        self.failIf(self.group_user.has_perm('change', self.obj))
        
        # Return False if 'delete' permission is not found for group user.
        self.failIf(self.group_user.has_perm('delete', self.obj))
       
        # Setup user share.
        UserShare.objects.create(
            user=self.user,
            can_view=True,
            can_change=True,
            can_delete=True,
            content_type=ContentType.objects.get_for_model(self.obj),
            object_id=self.obj.id,
        )
        
        # Return True if 'view' permission is found for user.
        self.failUnless(self.user.has_perm('view', self.obj))
        
        # Return True if 'change' permission is found for user.
        self.failUnless(self.user.has_perm('change', self.obj))
        
        # Return True if 'delete' permission is found for user.
        self.failUnless(self.user.has_perm('delete', self.obj))
       
       # Group share has not yet been setup, so should all still be unpermitted.
        # Return False if 'view' permission is not found for group user.
        self.failIf(self.group_user.has_perm('view', self.obj))
        
        # Return False if 'change' permission is not found for group user.
        self.failIf(self.group_user.has_perm('change', self.obj))
        
        # Return False if 'delete' permission is not found for group user.
        self.failIf(self.group_user.has_perm('delete', self.obj))
        
        # Setup group share.
        GroupShare.objects.create(
            group=self.group,
            can_view=True,
            can_change=True,
            can_delete=True,
            content_type=ContentType.objects.get_for_model(self.obj),
            object_id=self.obj.id,
        )
        
        # Return True if 'view' permission is found for group user.
        self.failUnless(self.group_user.has_perm('view', self.obj))
        
        # Return True if 'change' permission is found for group user.
        self.failUnless(self.group_user.has_perm('change', self.obj))
        
        # Return True if 'delete' permission is found for group user.
        self.failUnless(self.group_user.has_perm('delete', self.obj))

class ShareAdminTestCase(unittest.TestCase):
    def setUp(self):
        # Create test object, users, groups, admin object and request.
        self.obj = TestModel.objects.create(id=1)
        self.user = User.objects.create(username='user')
        self.group = Group.objects.create(name='group')
        self.group_user = User.objects.create(username='group_user')
        self.group_user.groups.add(self.group)
        self.group_user.save()
        self.request = RequestFactory().get('/')
        self.share_admin = TestModelAdmin(TestModel, admin.site)
    
    def tearDown(self):
        # Delete created objects.
        self.obj.delete()
        self.user.delete()
        self.group.delete()
        self.group_user.delete()
    
    def test_has_change_permission(self):
        # Anonymous user should never have change permission.
        self.failIf(self.share_admin.has_change_permission(self.request, self.obj))
        
        # Authenticated user without can_change permission should get False.
        self.request.user = self.user
        self.failIf(self.share_admin.has_change_permission(self.request, self.obj))
        
        # Authenticated user with can_change permission should get True.
        UserShare.objects.get_or_create(
            user=self.user,
            can_change=True,
            content_type=ContentType.objects.get_for_model(self.obj),
            object_id=self.obj.id,
        )
        self.failUnless(self.share_admin.has_change_permission(self.request, self.obj))
        
        # Authenticated group user without group having can_change permission should get False.
        self.request.user = self.group_user
        self.failIf(self.share_admin.has_change_permission(self.request, self.obj))
        
        # Authenticated group user with group having can_change permission should get True.
        GroupShare.objects.get_or_create(
            group=self.group,
            can_change=True,
            content_type=ContentType.objects.get_for_model(self.obj),
            object_id=self.obj.id,
        )
        self.failUnless(self.share_admin.has_change_permission(self.request, self.obj))
    
    def test_has_delete_permission(self):
        # Anonymous user should never have delete permission.
        self.failIf(self.share_admin.has_delete_permission(self.request, self.obj))
        
        # Authenticated user without can_delete permission should get False.
        self.request.user = self.user
        self.failIf(self.share_admin.has_delete_permission(self.request, self.obj))
        
        # Authenticated user with can_delete permission should get True.
        UserShare.objects.get_or_create(
            user=self.user,
            can_delete=True,
            content_type=ContentType.objects.get_for_model(self.obj),
            object_id=self.obj.id,
        )
        self.failUnless(self.share_admin.has_delete_permission(self.request, self.obj))
        
        # Authenticated group user without group having can_delete permission should get False.
        self.request.user = self.group_user
        self.failIf(self.share_admin.has_delete_permission(self.request, self.obj))
        
        # Authenticated group user with group having can_delete permission should get True.
        GroupShare.objects.get_or_create(
            group=self.group,
            can_delete=True,
            content_type=ContentType.objects.get_for_model(self.obj),
            object_id=self.obj.id,
        )
        self.failUnless(self.share_admin.has_delete_permission(self.request, self.obj))

    def test_queryset(self):
        # Anonymous user should always have an empty queryset
        self.failIf(self.share_admin.queryset(self.request))
        
        # Authenticated user without can_view permission should get an empty queryset.
        self.request.user = self.user
        self.failIf(self.share_admin.queryset(self.request))
        
        # Authenticated user with can_view permission should get queryset containing obj.
        UserShare.objects.get_or_create(
            user=self.user,
            can_view=True,
            content_type=ContentType.objects.get_for_model(self.obj),
            object_id=self.obj.id,
        )
        self.failUnless(self.obj in self.share_admin.queryset(self.request))
        
        # Authenticated group user without group having can_view permission should get an empty queryset.
        self.request.user = self.group_user
        self.failIf(self.share_admin.queryset(self.request))
        
        # Authenticated group user with group having can_view permission should get queryset containing obj.
        GroupShare.objects.get_or_create(
            group=self.group,
            can_view=True,
            content_type=ContentType.objects.get_for_model(self.obj),
            object_id=self.obj.id,
        )
        self.failUnless(self.obj in self.share_admin.queryset(self.request))

class UtilsTestCase(unittest.TestCase):
    def setUp(self):
        # Create test object, users and groups.
        self.obj = TestModel.objects.create(id=1)
        self.user = User.objects.create(username='user')
        self.group = Group.objects.create(name='group')
        self.group_user = User.objects.create(username='group_user')
        self.group_user.groups.add(self.group)
        self.group_user.save()
    
    def tearDown(self):
        # Delete created objects.
        self.obj.delete()
        self.user.delete()
        self.group.delete()
        self.group_user.delete()

    def test_limit_queryset_by_permission(self):
        # Return False if 'view' permission is not found for user.
        self.failIf(utils.limit_queryset_by_permission(TestModel.objects.all(), 'view', self.user))
        
        # Return False if 'change' permission is not found for user.
        self.failIf(utils.limit_queryset_by_permission(TestModel.objects.all(), 'change', self.user))
        
        # Return False if 'delete' permission is not found for user.
        self.failIf(utils.limit_queryset_by_permission(TestModel.objects.all(), 'delete', self.user))
        
        # Return False if 'view' permission is not found for group user.
        self.failIf(utils.limit_queryset_by_permission(TestModel.objects.all(), 'view', self.group_user))
        
        # Return False if 'change' permission is not found for group user.
        self.failIf(utils.limit_queryset_by_permission(TestModel.objects.all(), 'change', self.group_user))
        
        # Return False if 'delete' permission is not found for group user.
        self.failIf(utils.limit_queryset_by_permission(TestModel.objects.all(), 'delete', self.group_user))
       
        # Setup user share.
        UserShare.objects.create(
            user=self.user,
            can_view=True,
            can_change=True,
            can_delete=True,
            content_type=ContentType.objects.get_for_model(self.obj),
            object_id=self.obj.id,
        )
        
        # Return True if 'view' permission is found for user.
        self.failUnless(utils.limit_queryset_by_permission(TestModel.objects.all(), 'view', self.user))
        
        # Return True if 'change' permission is found for user.
        self.failUnless(utils.limit_queryset_by_permission(TestModel.objects.all(), 'change', self.user))
        
        # Return True if 'delete' permission is found for user.
        self.failUnless(utils.limit_queryset_by_permission(TestModel.objects.all(), 'delete', self.user))
       
        # Group share has not yet been setup, so should all still be unpermitted.
        # Return False if 'view' permission is not found for group user.
        self.failIf(utils.limit_queryset_by_permission(TestModel.objects.all(), 'view', self.group_user))
        
        # Return False if 'change' permission is not found for group user.
        self.failIf(utils.limit_queryset_by_permission(TestModel.objects.all(), 'change', self.group_user))
        
        # Return False if 'delete' permission is not found for group user.
        self.failIf(utils.limit_queryset_by_permission(TestModel.objects.all(), 'delete', self.group_user))
        
        # Setup group share.
        GroupShare.objects.create(
            group=self.group,
            can_view=True,
            can_change=True,
            can_delete=True,
            content_type=ContentType.objects.get_for_model(self.obj),
            object_id=self.obj.id,
        )
        
        # Return True if 'view' permission is found for group user.
        self.failUnless(utils.limit_queryset_by_permission(TestModel.objects.all(), 'view', self.group_user))
        
        # Return True if 'change' permission is found for group user.
        self.failUnless(utils.limit_queryset_by_permission(TestModel.objects.all(), 'change', self.group_user))
        
        # Return True if 'delete' permission is found for group user.
        self.failUnless(utils.limit_queryset_by_permission(TestModel.objects.all(), 'delete', self.group_user))

        # User should always have access to its own user object.
        self.failUnless(self.user in utils.limit_queryset_by_permission(User.objects.all(), 'view', self.user))
        self.failUnless(self.user in utils.limit_queryset_by_permission(User.objects.all(), 'change', self.user))
        self.failUnless(self.user in utils.limit_queryset_by_permission(User.objects.all(), 'delete', self.user))
        
        # User should never have access to other user objects.
        self.failIf(self.user in utils.limit_queryset_by_permission(User.objects.all(), 'view', self.group_user))
        self.failIf(self.user in utils.limit_queryset_by_permission(User.objects.all(), 'change', self.group_user))
        self.failIf(self.user in utils.limit_queryset_by_permission(User.objects.all(), 'delete', self.group_user))
