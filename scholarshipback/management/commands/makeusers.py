from django.core.management import BaseCommand
from django.contrib.auth.models import User, Permission
from ...models import Admin


class Command(BaseCommand):

    def handle(self, *args, **options):
        users = User.objects.filter(is_superuser=False)

        for user in users:
            user.delete()

        admins = Admin.objects.all()

        print(Permission.objects.all()[77].name)

        for admin in admins:
            user = User.objects.create_user(
                admin.login,
                admin.email,
                admin.password,
                first_name=admin.firstname,
                last_name=admin.lastname,
                is_staff=True
            )
            user.user_permissions.set([
                Permission.objects.get(name='Can add Тип повышенной стипендии').id,
                Permission.objects.get(name='Can change Тип повышенной стипендии').id,
                Permission.objects.get(name='Can delete Тип повышенной стипендии').id,
                Permission.objects.get(name='Can view Тип повышенной стипендии').id,

                Permission.objects.get(name='Can add Достижения').id,
                Permission.objects.get(name='Can change Достижения').id,
                Permission.objects.get(name='Can delete Достижения').id,
                Permission.objects.get(name='Can view Достижения').id,

                Permission.objects.get(name='Can add Вид достижения').id,
                Permission.objects.get(name='Can change Вид достижения').id,
                Permission.objects.get(name='Can delete Вид достижения').id,
                Permission.objects.get(name='Can view Вид достижения').id,

                Permission.objects.get(name='Can add Статус мероприятия').id,
                Permission.objects.get(name='Can change Статус мероприятия').id,
                Permission.objects.get(name='Can delete Статус мероприятия').id,
                Permission.objects.get(name='Can view Статус мероприятия').id,

                Permission.objects.get(name='Can add Уровень достижения').id,
                Permission.objects.get(name='Can change Уровень достижения').id,
                Permission.objects.get(name='Can delete Уровень достижения').id,
                Permission.objects.get(name='Can view Уровень достижения').id,
            ])

        print(f'{len(admins)} django users was/were created')
