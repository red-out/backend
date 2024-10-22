class UserSingleton:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = UserSingleton()
        return cls._instance

    def get_user(self):
        # Здесь возвращаем фиксированного пользователя, например, по ID
        # Замените на вашу логику получения пользователя
        from django.contrib.auth.models import User
        return User.objects.get(pk=1)  # Предположим, что это ID фиксированного пользователя
