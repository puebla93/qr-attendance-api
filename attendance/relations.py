from rest_framework.serializers import RelatedField


class FunctionRelatedField(RelatedField):
    """
        A read only field that represents its targets using the return value of
        provide function name.
    """

    def __init__(self, func_name, **kwargs):
        assert func_name is not None, 'The `func_name` argument is required.'
        self.func_name = func_name
        kwargs['read_only'] = True
        super().__init__(**kwargs)

    def to_representation(self, obj):
        func = getattr(obj, self.func_name)
        return func() if func else None
