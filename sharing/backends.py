
class SharingBackend(object):
    # Advertise capabilities.
    supports_object_permissions = True
    supports_anonymous_user = True

    def authenticate(self, username, password):
        """
        Required by Django, does nothing.
        """
        return None

    def has_perm(self, user_obj, perm, obj=None):
        return True
