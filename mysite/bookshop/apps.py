from django.apps import AppConfig


class BookshopConfig(AppConfig):
    name = 'bookshop'

    def ready(self):
        import bookshop.signals