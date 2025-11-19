"""
URL configuration for NewsPaper project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler403
from django.views.generic import TemplateView

from django.views.generic import TemplateView
import logging

# Создаем логгер для тестирования
logger = logging.getLogger('news')


def test_logs(request):
    """Страница для тестирования логирования"""
    # Тестируем разные уровни логирования
    logger.debug("Это DEBUG сообщение - для отладки")
    logger.info("Это INFO сообщение - обычная информация")
    logger.warning("Это WARNING сообщение - предупреждение")
    logger.error("Это ERROR сообщение - ошибка")

    try:
        # Создаём ошибку для теста
        result = 1 / 0
    except Exception as e:
        logger.exception("Это CRITICAL сообщение с ошибкой")

    from django.http import HttpResponse
    return HttpResponse("Логи в консоли и файлах в папке logs/!")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('news/', include('news.urls')),
    path('accounts/', include('allauth.urls')),
    path('debug-signup/', TemplateView.as_view(template_name='debug_signup.html'), name='debug_signup'),
    path('test-logs/', test_logs, name='test_logs'),
]
handler403 = 'news.views.custom_permission_denied'