from django.apps import AppConfig
from django.utils.translation import (
    gettext_lazy as _,
)  # импортируем функцию перевода


class BlogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "blog"
    verbose_name = _("Блог")  # русское название приложения для админки
