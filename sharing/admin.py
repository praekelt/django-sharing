from django.contrib.contenttypes import generic

from sharing.models import GroupShare, UserShare

class GroupShareInline(generic.GenericTabularInline):
    """
    Group share inline admin class.
    """
    extra = 1
    model = GroupShare

class UserShareInline(generic.GenericTabularInline):
    """
    User share inline admin class.
    """
    extra = 1
    model = UserShare

class SharingAdminMixin(object):
    """
    Mixin class limiting admin content access based on object and user permissions.
    """
    def has_change_permission(self, request, obj=None):
        """
        Returns True if the given request has permission to change the given
        Django model instance or object.

        If `obj` is None, this should return True if the given request has
        permission to change *any* object of the given type.
        """
        opts = self.opts
        return request.user.has_perm(opts.app_label + '.' + opts.get_change_permission(), obj)

    def has_delete_permission(self, request, obj=None):
        """
        Returns True if the given request has permission to change the given
        Django model instance or object.

        If `obj` is None, this should return True if the given request has
        permission to delete *any* object of the given type.
        """
        opts = self.opts
        return request.user.has_perm(opts.app_label + '.' + opts.get_delete_permission(), obj)
    
    def queryset(self, request):
        """
        Returns a QuerySet of all model instances that can be edited by the
        admin site. This is used by changelist_view.
        """
        qs = self.model._default_manager.get_query_set()
        # TODO: this should be handled by some parameter to the ChangeList.
        ordering = self.ordering or () # otherwise we might try to *None, which is bad ;)
        if ordering:
            qs = qs.order_by(*ordering)

        # Filter objects based on can_view permission.
        # Superusers can view all objects.
        if request.user.is_superuser:
            return qs
        else:
            # TODO: There must be a more efficient way to do this, refactor.
            filtered_object_ids = []
            for obj in qs:
                if request.user.has_perm(self.opts.app_label + '.view', obj):
                    filtered_object_ids.append(obj.id)
            return qs.filter(id__in=filtered_object_ids)
