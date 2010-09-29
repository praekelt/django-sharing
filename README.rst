Django Sharing
==============

**Django row level sharing app limiting content access by user in Django admin.**

Features
--------
#. Provides admin view, change and delete permissions, restricting content access and limiting available actions per user.
#. Filters ``ForeignKey`` fields by view permissions. 
#. Filters ``ManyToManyField`` fields by view permissions. 
#. Automatically enables sharing on all admin classes (optional). 

Installation
------------

#. Install or add django-sharing to your python path.
#. Add ``'sharing'`` to the project's ``INSTALLED_APPS`` setting.
#. Add ``'sharing.backends.SharingBackend'`` to the project's ``AUTHENTICATION_BACKENDS`` setting.

Usage
-----

In order for django-sharing to limit content access your various admin classes need to include the ``ShareAdminMixin`` class. For example::
    
    # admin.py
    from django.contrib import admin
    from sharing.admin import ShareAdminMixin

    class ArticleAdmin(ShareAdminMixin, admin.ModelAdmin):
        pass

    admin.site.register(Article, ArticleAdmin)

It is crucial for ``ShareAdminMixin`` to be the first ancestor class in the admin class' definition.  

Alternatively you can automatically enable sharing for all models registered with the admin site. django-sharing includes an ``admin_mixin_share`` method which will apply the ``ShareAdminMixin`` class to all models registered with the admin site. Call the method *after* ``admin.autodiscover()`` in urls.py::

    # urls.py
    from django.conf.urls.defaults import *
    from django.contrib import admin
    
    import sharing

    admin.autodiscover()
    sharing.admin_mixin_share()

    urlpatterns = patterns('',
        (r'^admin/', include(admin.site.urls)),
    )

Once the ``ShareAdminMixin`` class has been applied your admin change views should include ``Group`` and ``User`` share inlines and restrict content appropriately.

