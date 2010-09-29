def limit_queryset_by_permission(qs, perm, user):
    """
    Filter queryset by user permission.
    """
    # TODO: There must be a more efficient way to do this, refactor.
    filtered_object_ids = []
    for obj in qs:
        # User always has access to herself.
        if obj == user:
            filtered_object_ids.append(obj.id)
            continue
        if user.has_perm(perm, obj):
            filtered_object_ids.append(obj.id)
    return qs.filter(id__in=filtered_object_ids)
