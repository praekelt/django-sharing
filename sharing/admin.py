from django.contrib import admin
from django.contrib.admin import widgets
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from sharing import utils
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

class ShareAdminMixin(object):
    """
    Admin class limiting admin content access based on object and user permissions and 
    providing user and group permission inlines.
    """
    inlines = [
        GroupShareInline,
        UserShareInline,
    ]

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """
        Get a form Field for a ForeignKey.
        """
        db = kwargs.get('using')
        if db_field.name in self.raw_id_fields:
            kwargs['widget'] = widgets.ForeignKeyRawIdWidget(db_field.rel, using=db)
        elif db_field.name in self.radio_fields:
            kwargs['widget'] = widgets.AdminRadioSelect(attrs={
                'class': get_ul_class(self.radio_fields[db_field.name]),
            })
            kwargs['empty_label'] = db_field.blank and _('None') or None
       
        # Limit queryset by permissions.
        kwargs['queryset'] = utils.limit_queryset_by_permission(
            qs=db_field.rel.to.objects.all(), 
            perm=self.opts.app_label + '.view', 
            user=request.user,
        )

        return db_field.formfield(**kwargs)
    
    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        """
        Get a form Field for a ManyToManyField.
        """
        # If it uses an intermediary model that isn't auto created, don't show
        # a field in admin.
        if not db_field.rel.through._meta.auto_created:
            return None
        db = kwargs.get('using')
    
        if db_field.name in self.raw_id_fields:
            kwargs['widget'] = widgets.ManyToManyRawIdWidget(db_field.rel, using=db)
            kwargs['help_text'] = ''
        elif db_field.name in (list(self.filter_vertical) + list(self.filter_horizontal)):
            kwargs['widget'] = widgets.FilteredSelectMultiple(db_field.verbose_name, (db_field.name in self.filter_vertical))
   
        # Limit queryset by permissions.
        kwargs['queryset'] = utils.limit_queryset_by_permission(
            qs=db_field.rel.to.objects.all(), 
            perm=self.opts.app_label + '.view', 
            user=request.user,
        )

        return db_field.formfield(**kwargs)
    
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
            return utils.limit_queryset_by_permission(
                qs=qs, 
                perm=self.opts.app_label + '.view', 
                user=request.user,
            )
    
    def save_model(self, request, obj, form, change):
        """
        On admin save create full share for requesting user.
        """
        super(ShareAdminMixin, self).save_model(request, obj, form, change)
        
        # Setup full share if it does not already exist.
        try:
            UserShare.objects.get(
                user=request.user,
                content_type=ContentType.objects.get_for_model(obj),
                object_id=obj.id,
            )
        except UserShare.DoesNotExist:
            UserShare.objects.create(
                user=request.user,
                can_view=True,
                can_change=True,
                can_delete=True,
                content_type=ContentType.objects.get_for_model(obj),
                object_id=obj.id,
            )
