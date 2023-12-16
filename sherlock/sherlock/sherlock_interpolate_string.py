def interpolate_string(object, username):
    """Insert a string into the string properties of an object recursively."""

    if isinstance(object, str):
        return object.replace("{}", username)
    elif isinstance(object, dict):
        for key, value in object.items():
            object[key] = interpolate_string(value, username)
    elif isinstance(object, list):
        for i in object:
            object[i] = interpolate_string(object[i], username)

    return object