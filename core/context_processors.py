def has_group_permission(request):
    def check_group(group_name):
        return request.user.groups.filter(name=group_name).exists()
    
    return {'has_group_permission': check_group}