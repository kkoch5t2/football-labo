from django.apps import AppConfig


class SoccerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'soccer'
    verbose_name = 'アプリ機能'

    def ready(self):
        from soccer.tasks.task import start
        start()