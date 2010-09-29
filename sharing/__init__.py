import inspect

def admin_mixin_share():
    """
    Apply ShareAdminMixin class to registered admin classes, thus automatically enabling 
    sharing on for all models in admin.
    """
    from django.contrib import admin
    from sharing.admin import ShareAdminMixin

    for model_class, admin_options in admin.site._registry.items():
        admin_class = admin_options.__class__
       
        # Bypass mixin if share mixin already in bases. 
        if ShareAdminMixin in inspect.getmro(admin_class):
            continue
        
        # Unregister existing admin.
        admin.site.unregister(model_class)

        # Create mixin admin class.
        mixin_admin_class = type("%sShareMixin" % admin_class.__name__, (ShareAdminMixin, admin_class,), {'inlines': admin_class.inlines + ShareAdminMixin.inlines})
        
        # Register new admin with sharing mixin.
        admin.site.register(model_class, mixin_admin_class)
