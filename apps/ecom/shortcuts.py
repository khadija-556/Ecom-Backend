from django.core.exceptions import ObjectDoesNotExist

def get_object_or_false(model, *args, **kwargs):
    """
    A custom function to retrieve an object or return False if it doesn't exist.
    
    :param model: The Django model class to query.
    :param args: Positional arguments for the query.
    :param kwargs: Keyword arguments for the query.
    :return: The object if found, otherwise False.
    """
    try:
        return model.objects.get(*args, **kwargs)
    except ObjectDoesNotExist:
        return False