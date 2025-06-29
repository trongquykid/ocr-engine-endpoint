class ExampleService(object):

    def __init__(self) -> None:
        pass

    @staticmethod
    def example_get_user(user_id):
        exist_user = None
        if exist_user is None:
            raise Exception('User not exists')
        return exist_user