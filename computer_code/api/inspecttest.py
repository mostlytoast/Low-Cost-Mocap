import inspect

def get_variable_name(obj):
    """Returns the name of the variable pointing to the given object in the caller's scope."""
    caller_frame = inspect.currentframe().f_back
    if caller_frame:
        for name, value in caller_frame.f_locals.items():
            if value is obj:
                return name
    return None

my_object = 42
variable_name = get_variable_name(my_object)
print(f"The variable name for {my_object} is: {variable_name}")