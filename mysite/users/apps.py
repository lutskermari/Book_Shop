from django.apps import AppConfig
from django.db.models.signals import post_migrate

def create_default_groups(sender, **kwargs):
    from django.contrib.auth.models import Group, Permission
    managers_group, _ = Group.objects.get_or_create(name='Managers')
    Group.objects.get_or_create(name='Regular Users')
    
    book_permissions = Permission.objects.filter(
        content_type__app_label='bookshop',
        codename__in=['add_book', 'change_book', 'delete_book']
    )
    
    managers_group.permissions.set(book_permissions)

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        post_migrate.connect(create_default_groups, sender=self)
