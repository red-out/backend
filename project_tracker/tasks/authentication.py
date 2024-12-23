import redis
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import CustomUser  # Импортируйте кастомную модель пользователя
import logging
from django.shortcuts import get_object_or_404
# Настройки для подключения к Redis
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
session_storage = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

logger = logging.getLogger(__name__)

class RedisSessionAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # Проверяем наличие session_id в заголовках
        session_id = request.headers.get('session_id')

        # Если его нет, проверяем куки
        if not session_id:
            session_id = request.COOKIES.get('session_id')

        logger.debug(f'Session ID from request: {session_id}')

        if not session_id:
            logger.debug('No session_id provided in headers or cookies.')
            return None  # Возвращаем None, если session_id отсутствует

        # Проверяем наличие session_id в Redis
        username = session_storage.get(session_id)

        if not username:
            raise AuthenticationFailed('Invalid session_id')

        # Извлекаем пользователя из базы данных
        user = get_object_or_404(CustomUser, email=username)

        # Возвращаем пользователя и None (вместо строки)
        return (user, None)