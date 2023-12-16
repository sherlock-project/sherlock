def check_for_parameter(username):
    '''checks if {?} exists in the username
    if exist it means that sherlock is looking for more multiple username'''
    return ("{?}" in username)
