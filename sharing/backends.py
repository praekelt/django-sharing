from django.contrib.contenttypes.models import ContentType

from sharing.models import GroupShare,  UserShare

class SharingBackend(object):
    """
    Authentication backend providing row level permissions.
    """

    # Advertise capabilities.
    supports_object_permissions = True
    supports_anonymous_user = True

    def authenticate(self, username, password):
        """
        Required by Django, does nothing.
        """
        return None

    def has_perm(self, user_obj, perm, obj=None):
        """
        Checks whether or not the given user or her groups has the given 
        permission for the given object. 
        """
        # Ignore check without obj.
        if obj is None:
            return False

        # Ignore if user is not authenticated .
        if not user_obj.is_authenticated():
            return False

        # Resolve permission.
        try:
            perm = 'can_%s' % perm.split('.')[-1].split('_')[0]
        except IndexError:
            return False
            
        # Find shares for user and object content types.
        content_type = ContentType.objects.get_for_model(obj)
        user_shares = UserShare.objects.filter(
            content_type=content_type,
            object_id=obj.id,
            user=user_obj,
        )

        # Return true if user has permission.
        if user_shares.filter(**{perm: True}).exists():
            return True
        
        # Find shares for user group and object content types.
        group_shares = GroupShare.objects.filter(
            content_type=content_type,
            object_id=obj.id,
            group__in=user_obj.groups.all(),
        )

        # Return true if user group has permission.
        if group_shares.filter(**{perm: True}).exists():
            return True

        return False
