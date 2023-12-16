def multiple_usernames(username):
    checksymbols = []
    checksymbols = ["_", "-", "."]

    '''replace the parameter with with symbols and return a list of usernames'''
    allUsernames = []
    for i in checksymbols:
        allUsernames.append(username.replace("{?}", i))
    return allUsernames